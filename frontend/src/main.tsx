import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";

export function main(): void {
  const rootElement = document.getElementById("root");
  if (rootElement === null) {
    throw new Error("root element missing");
  }
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}

main();
