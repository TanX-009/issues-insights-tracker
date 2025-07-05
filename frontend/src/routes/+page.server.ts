import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals }) => {
  try {
    return { user: locals.user };
  } catch (e) {
    return {
      issues: [],
      error: e instanceof Error ? e.message : "Unknown error occurred",
    };
  }
};
