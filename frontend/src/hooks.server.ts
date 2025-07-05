import { redirect } from "@sveltejs/kit";
import type { Handle } from "@sveltejs/kit";

const EXACT_PROTECTED_ROUTES = ["/"]; // strictly equal to
const PREFIX_PROTECTED_ROUTES = ["/issues", "/logout", "/users"]; // startsWith

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get("auth_token");
  const user = event.cookies.get("auth");
  const pathname = event.url.pathname;

  const isProtected =
    EXACT_PROTECTED_ROUTES.includes(pathname) ||
    PREFIX_PROTECTED_ROUTES.some((r) => pathname.startsWith(r));

  // Redirect unauthenticated access to protected routes
  if (!token && isProtected) {
    throw redirect(303, "/login");
  }

  // Set token and user on locals
  if (token) event.locals.token = token;
  if (user) event.locals.user = JSON.parse(user);

  // Redirect authenticated users away from login
  if (token && pathname === "/login") {
    throw redirect(303, "/");
  }

  return resolve(event);
};
