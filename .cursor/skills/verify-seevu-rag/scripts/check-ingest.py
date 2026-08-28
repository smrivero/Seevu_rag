import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

origin = os.environ.get("SEEVU_ORIGIN", "http://localhost:8080").rstrip("/")
evidence = pathlib.Path(os.environ.get("SEEVU_EVIDENCE", "."))
root = pathlib.Path(os.environ.get("SEEVU_ROOT", "."))
fixture = pathlib.Path(
    os.environ.get(
        "SEEVU_FIXTURE_PDF",
        str(root / ".cursor/skills/verify-seevu-rag/fixtures/sample.pdf"),
    )
)
mode = sys.argv[1] if len(sys.argv) > 1 else "upload"


def get_json(url: str) -> tuple[int, object]:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def post_pdf(url: str, path: pathlib.Path) -> tuple[int, object]:
    boundary = "----seevu" + os.urandom(8).hex()
    payload = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        "Content-Type: application/pdf\r\n"
        "\r\n"
    ).encode("utf-8") + payload + f"\r\n--{boundary}--\r\n".encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            print(f"check-ingest: {url} status {exc.code} body {raw!r}", file=sys.stderr)
            sys.exit(1)
        print(
            f"check-ingest: {url} status {exc.code} detail={parsed.get('detail')!r}",
            file=sys.stderr,
        )
        sys.exit(1)


def require_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise SystemExit(f"check-ingest: {label} is {value!r}")
    return value


def listed_ids(body: object) -> list[str]:
    payload = require_object(body, "GET /api/documents")
    documents = payload.get("documents")
    if not isinstance(documents, list):
        raise SystemExit(f"check-ingest: documents is {documents!r}")
    ids: list[str] = []
    for item in documents:
        if not isinstance(item, dict):
            raise SystemExit("check-ingest: document entry is not an object")
        document_id = item.get("document_id")
        if isinstance(document_id, str):
            ids.append(document_id)
    return ids


def check_upload() -> None:
    if not fixture.is_file():
        raise SystemExit(f"check-ingest: missing fixture {fixture}")
    status, body = post_pdf(f"{origin}/api/documents", fixture)
    if status != 200:
        raise SystemExit(f"check-ingest: POST status {status}")
    record = require_object(body, "POST /api/documents")
    document_id = record.get("document_id")
    pages = record.get("pages")
    chunks = record.get("chunks")
    if not isinstance(document_id, str) or not document_id:
        raise SystemExit(f"check-ingest: missing document_id in {record!r}")
    if not isinstance(pages, int) or pages <= 0:
        raise SystemExit(f"check-ingest: pages must be > 0, got {pages!r}")
    if not isinstance(chunks, int) or chunks <= 0:
        raise SystemExit(f"check-ingest: chunks must be > 0, got {chunks!r}")
    if record.get("status") != "indexed":
        raise SystemExit(f"check-ingest: status is {record.get('status')!r}")

    list_status, listed = get_json(f"{origin}/api/documents")
    if list_status != 200:
        raise SystemExit(f"check-ingest: GET status {list_status}")
    if document_id not in listed_ids(listed):
        raise SystemExit("check-ingest: GET /api/documents is missing the uploaded document")

    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "ingest.json").write_text(
        json.dumps(record, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    sys.stdout.write(json.dumps(record, separators=(",", ":")))
    sys.stdout.write("\n")


def check_listed() -> None:
    ingest_path = evidence / "ingest.json"
    record = require_object(
        json.loads(ingest_path.read_text(encoding="utf-8")),
        "ingest.json",
    )
    document_id = record.get("document_id")
    if not isinstance(document_id, str):
        raise SystemExit("check-ingest: ingest.json is missing document_id")
    status, listed = get_json(f"{origin}/api/documents")
    if status != 200:
        raise SystemExit(f"check-ingest: GET status {status}")
    if document_id not in listed_ids(listed):
        raise SystemExit("check-ingest: document did not survive backend restart")
    print(json.dumps({"document_id": document_id, "persisted": True}, separators=(",", ":")))


if mode == "listed":
    check_listed()
elif mode == "upload":
    check_upload()
else:
    raise SystemExit(f"check-ingest: unknown mode {mode!r}")
