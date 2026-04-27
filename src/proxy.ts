import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const secret = process.env.KEYSTATIC_SECRET;

  // If no secret is configured, block access entirely in production
  if (!secret) {
    if (process.env.NODE_ENV === "production") {
      return new NextResponse("Admin disabled: KEYSTATIC_SECRET not set.", { status: 403 });
    }
    return NextResponse.next();
  }

  const auth = request.headers.get("authorization");
  if (auth) {
    const [scheme, encoded] = auth.split(" ");
    if (scheme === "Basic" && encoded) {
      const decoded = Buffer.from(encoded, "base64").toString("utf-8");
      const colon = decoded.indexOf(":");
      const username = decoded.slice(0, colon);
      const password = decoded.slice(colon + 1);
      if (username === process.env.KEYSTATIC_USER && password === secret) {
        return NextResponse.next();
      }
    }
  }

  return new NextResponse("Unauthorized", {
    status: 401,
    headers: { "WWW-Authenticate": `Basic realm="AI Pulse Admin"` },
  });
}

export const config = {
  matcher: ["/keystatic/:path*", "/api/keystatic/:path*"],
};

