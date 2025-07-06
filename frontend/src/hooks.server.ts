import { redirect } from "@sveltejs/kit";
import type { Handle } from "@sveltejs/kit";
import { base } from "$app/paths";

const EXACT_PROTECTED_ROUTES = [base + "/"]; // strictly equal to
const PREFIX_PROTECTED_ROUTES = [
  base + "/issues",
  base + "/logout",
  base + "/users",
]; // startsWith

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get("auth_token");
  const user = event.cookies.get("auth");
  const pathname = event.url.pathname;

  const isProtected =
    EXACT_PROTECTED_ROUTES.includes(pathname) ||
    PREFIX_PROTECTED_ROUTES.some((r) => pathname.startsWith(r));

  // Redirect unauthenticated access to protected routes
  if (!token && isProtected) {
    throw redirect(303, base + "/login");
  }

  // Set token and user on locals
  if (token) event.locals.token = token;
  if (user) event.locals.user = JSON.parse(user);

  // Redirect authenticated users away from login
  if (token && pathname === base + "/login") {
    throw redirect(303, base + "/");
  }

  return resolve(event);
};
