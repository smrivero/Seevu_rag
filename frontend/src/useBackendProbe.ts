import { isAxiosError, isCancel } from "axios";
import type { AxiosInstance } from "axios";
import { useEffect, useState } from "react";

import { apiClient } from "./apiClient";

export type ProbeFailure =
  | { kind: "transport" }
  | { kind: "http"; status: number }
  | { kind: "protocol" };

export type ProbeResult =
  | { kind: "live" }
  | { kind: "down"; failure: ProbeFailure };

export type ProbeState = { kind: "checking" } | ProbeResult;

type HealthDocument = { readonly status: "ok" };

export function parseHealthPayload(data: unknown): HealthDocument {
  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    throw new Error("health payload is not an object");
  }
  if (!("status" in data) || data.status !== "ok") {
    throw new Error("health payload status is not ok");
  }
  return { status: "ok" };
}

export async function probeHealth(args: {
  client: AxiosInstance;
  signal: AbortSignal;
}): Promise<ProbeResult> {
  try {
    const response = await args.client.get<unknown>("/health", {
      signal: args.signal,
    });
    if (response.status !== 200) {
      return { kind: "down", failure: { kind: "http", status: response.status } };
    }
    try {
      parseHealthPayload(response.data);
    } catch {
      return { kind: "down", failure: { kind: "protocol" } };
    }
    return { kind: "live" };
  } catch (error: unknown) {
    if (isCancel(error)) {
      throw error;
    }
    if (isAxiosError(error) && error.response !== undefined) {
      return {
        kind: "down",
        failure: { kind: "http", status: error.response.status },
      };
    }
    return { kind: "down", failure: { kind: "transport" } };
  }
}

export function useBackendProbe(): ProbeState {
  const [state, setState] = useState<ProbeState>({ kind: "checking" });

  useEffect(() => {
    const controller = new AbortController();
    let stillMounted = true;

    void probeHealth({ client: apiClient, signal: controller.signal })
      .then((result) => {
        if (stillMounted) {
          setState(result);
        }
      })
      .catch((error: unknown) => {
        if (!stillMounted || isCancel(error)) {
          return;
        }
        setState({ kind: "down", failure: { kind: "transport" } });
      });

    return () => {
      stillMounted = false;
      controller.abort();
    };
  }, []);

  return state;
}
