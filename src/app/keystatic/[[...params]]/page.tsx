"use client";

import { Keystatic } from "@keystatic/core/ui";
import keystaticConfig from "../../../../keystatic.config";

export default function KeystaticPage() {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 50 }}>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <Keystatic config={keystaticConfig as any} />
    </div>
  );
}
