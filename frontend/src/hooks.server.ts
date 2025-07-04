import { redirect } from "@sveltejs/kit";
import type { Handle } from "@sveltejs/kit";

const PROTECTED_ROUTES = ["/issues"]; // secured pages

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get("auth_token");
  const pathname = event.url.pathname;

  // Set token on locals for later use
  event.locals.token = token;

  // Redirect unauthenticated access to protected routes
  if (!token && PROTECTED_ROUTES.some((r) => pathname.startsWith(r))) {
    throw redirect(303, "/login");
  }

  // Redirect authenticated users away from login
  if (token && pathname === "/login") {
    throw redirect(303, "/"); // or homepage, dashboard etc.
  }

  return resolve(event);
};
