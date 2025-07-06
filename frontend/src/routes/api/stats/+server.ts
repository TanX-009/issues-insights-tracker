import { json, type RequestHandler } from "@sveltejs/kit";
import { get } from "$lib/api/config";
import Urls from "$lib/api/urls";
import type { TStat } from "$lib/types/stat";

export const GET: RequestHandler = async ({ locals }) => {
  const token = locals.token;

  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await get<TStat[], "">(Urls.getDailyStats, {
    Authorization: `Bearer ${token}`,
  });

  return json(response);
};
