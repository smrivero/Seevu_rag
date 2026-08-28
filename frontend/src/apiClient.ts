import axios, { type AxiosInstance } from "axios";

export const HEALTH_PROBE_TIMEOUT_MS = 3000;

export function createApiClient(): AxiosInstance {
  return axios.create({
    baseURL: "/api",
    timeout: HEALTH_PROBE_TIMEOUT_MS,
    headers: { Accept: "application/json" },
  });
}

export const apiClient: AxiosInstance = createApiClient();
