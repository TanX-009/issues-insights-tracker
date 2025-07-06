import { redirect, type ServerLoad } from "@sveltejs/kit";
import { base } from "$app/paths";

// export const GET: RequestHandler = async ({ cookies }) => {
//   cookies.delete("auth_token", { path: "/" });
//   cookies.delete("auth", { path: "/" });
//
//   throw redirect(302, base + "/login");
// };

export const load: ServerLoad = ({ cookies }) => {
  cookies.delete("auth_token", { path: "/" });
  cookies.delete("auth", { path: "/" });

  redirect(302, base + "/login");
};
