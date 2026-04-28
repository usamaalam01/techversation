import { draftMode } from "next/headers";
import { redirect } from "next/navigation";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get("secret");
  const slug = searchParams.get("slug");

  if (!slug) {
    return new Response("Missing slug", { status: 400 });
  }

  if (secret !== process.env.NEXT_PUBLIC_PREVIEW_SECRET) {
    return new Response("Invalid preview secret", { status: 401 });
  }

  const { enable } = await draftMode();
  enable();

  redirect(`/blog/${slug}`);
}
