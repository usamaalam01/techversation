import type { NextConfig } from "next";
import { buildSearchIndex } from "./src/lib/posts";
import fs from "fs";
import path from "path";

function writeSearchIndex() {
  const index = buildSearchIndex();
  const outDir = path.join(process.cwd(), "public");
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, "search-index.json"), JSON.stringify(index));
}

writeSearchIndex();

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.githubusercontent.com" },
      { protocol: "https", hostname: "images.unsplash.com" },
    ],
  },
};

export default nextConfig;
