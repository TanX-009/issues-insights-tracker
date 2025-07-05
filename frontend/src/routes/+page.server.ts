import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals, cookies }) => {
  try {
    const token = cookies.get("auth_token");
    return { user: locals.user, token };
  } catch (e) {
    return {
      issues: [],
      error: e instanceof Error ? e.message : "Unknown error occurred",
    };
  }
};
