#!/usr/bin/env node
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";

const origin = (process.env.SEEVU_ORIGIN ?? "http://localhost:8080").replace(
  /\/$/,
  "",
);
const evidenceDir = process.env.SEEVU_EVIDENCE;
if (!evidenceDir) {
  console.error("browser.mjs: SEEVU_EVIDENCE is required");
  process.exit(1);
}

const titleExpected = "RAG Intelligence Platform";
const connectedExpected = "Backend: Connected";

async function launchBrowser() {
  try {
    return await chromium.launch({ channel: "chrome", headless: true });
  } catch {
    return await chromium.launch({ headless: true });
  }
}

await mkdir(evidenceDir, { recursive: true });

const browser = await launchBrowser();
const page = await browser.newPage();
try {
  await page.goto(origin + "/", { waitUntil: "domcontentloaded" });
  await page.getByText(connectedExpected, { exact: true }).waitFor({
    state: "visible",
    timeout: 15_000,
  });

  const title = await page.title();
  if (title !== titleExpected) {
    throw new Error(`document title is ${JSON.stringify(title)}`);
  }

  const heading = page.getByRole("heading", {
    name: titleExpected,
    level: 1,
  });
  await heading.waitFor({ state: "visible" });

  const mainText = (await page.locator("main").innerText()).trim();
  if (!mainText.includes(titleExpected)) {
    throw new Error("main is missing RAG Intelligence Platform");
  }
  if (!mainText.includes(connectedExpected)) {
    throw new Error("main is missing Backend: Connected");
  }
  if (mainText.includes("Backend: Checking")) {
    throw new Error("main still shows Backend: Checking");
  }
  if (mainText.includes("Backend: Unavailable")) {
    throw new Error("main shows Backend: Unavailable");
  }

  await writeFile(path.join(evidenceDir, "health-status.txt"), mainText + "\n");
  await page.screenshot({
    path: path.join(evidenceDir, "health-status.png"),
    fullPage: true,
  });
} finally {
  await browser.close();
}
