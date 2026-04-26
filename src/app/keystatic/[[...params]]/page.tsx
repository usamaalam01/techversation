"use client";

import { Keystatic } from "@keystatic/core/ui";
import keystaticConfig from "../../../../keystatic.config";

export default function KeystaticPage() {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 50 }}>
      <Keystatic
        config={keystaticConfig}
        appSlug={{ envName: "NEXT_PUBLIC_KEYSTATIC_GITHUB_APP_SLUG", value: undefined }}
      />
    </div>
  );
}
