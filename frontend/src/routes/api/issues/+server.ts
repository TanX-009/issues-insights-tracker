import { json, type RequestHandler } from "@sveltejs/kit";
import { get } from "$lib/api/config";
import Urls from "$lib/api/urls";
import type { TIssue } from "$lib/types/issue"; // adjust the path and name based on your actual type
import handleResponse from "$lib/utils/response";

export const GET: RequestHandler = async ({ locals }) => {
  const token = locals.token;

  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await get<TIssue[], "">(Urls.getIssues, {
    Authorization: `Bearer ${token}`,
  });

  return handleResponse(response);
};
