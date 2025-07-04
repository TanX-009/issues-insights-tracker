import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const res = await fetch("/api/issues");

    if (!res.ok) {
      return {
        issues: [],
        error: `Failed to fetch issues: ${res.status} ${res.statusText}`,
      };
    }

    const issues = await res.json();
    return { issues };
  } catch (e) {
    return {
      issues: [],
      error: e instanceof Error ? e.message : "Unknown error occurred",
    };
  }
};
