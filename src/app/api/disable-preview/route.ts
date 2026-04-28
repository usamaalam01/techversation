import { draftMode } from "next/headers";
import { redirect } from "next/navigation";

export async function GET() {
  const { disable } = await draftMode();
  disable();
  redirect("/");
}
