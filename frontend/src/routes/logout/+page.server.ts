import { redirect, type ServerLoad } from "@sveltejs/kit";

// export const GET: RequestHandler = async ({ cookies }) => {
//   cookies.delete("auth_token", { path: "/" });
//   cookies.delete("auth", { path: "/" });
//
//   throw redirect(302, "/login");
// };

export const load: ServerLoad = ({ cookies }) => {
  cookies.delete("auth_token", { path: "/" });
  cookies.delete("auth", { path: "/" });

  redirect(302, "/login");
};
