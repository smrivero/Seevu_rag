import type { JSX } from "react";

import { BackendStatus } from "./BackendStatus";
import { useBackendProbe } from "./useBackendProbe";

export function App(): JSX.Element {
  const probe = useBackendProbe();
  return (
    <main>
      <h1>RAG Intelligence Platform</h1>
      <BackendStatus probe={probe} />
    </main>
  );
}
