import type { JSX } from "react";

import type { ProbeState } from "./useBackendProbe";

export function BackendStatus(props: { probe: ProbeState }): JSX.Element {
  switch (props.probe.kind) {
    case "checking":
      return <p>Backend: Checking</p>;
    case "live":
      return <p>Backend: Connected</p>;
    case "down":
      return <p>Backend: Unavailable</p>;
    default: {
      const _exhaustive: never = props.probe;
      return _exhaustive;
    }
  }
}
