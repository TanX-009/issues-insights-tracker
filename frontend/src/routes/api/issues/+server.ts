import { json, type RequestHandler } from "@sveltejs/kit";
import { delete_, get, post, put } from "$lib/api/config";
import Urls from "$lib/api/urls";
import type { TIssue } from "$lib/types/issue";

interface TCreateIssueRequest {
  title: string;
  description: string;
}

interface TUpdateIssueRequest {
  title: string;
  description: string;
  severity: TIssue["severity"];
  status: TIssue["status"];
}

export const GET: RequestHandler = async ({ locals }) => {
  const token = locals.token;

  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await get<TIssue[], "">(Urls.getIssues, {
    Authorization: `Bearer ${token}`,
  });

  return json(response);
};

export const POST: RequestHandler = async ({ request, locals }) => {
  const token = locals.token;

  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await post<FormData, TIssue, "">(
    Urls.createIssue,
    await request.formData(),
    {
      contentType: "application/x-www-form-urlencoded",
      Authorization: `Bearer ${token}`,
    },
  );

  return json(response);
};

export const PUT: RequestHandler = async ({ request, locals }) => {
  const { title, description, severity, status, id } = await request.json();
  const token = locals.token;

  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await put<TUpdateIssueRequest, TIssue, "">(
    Urls.updateIssue.replace("$$issue_id$$", id),
    {
      title,
      description,
      severity,
      status,
    },
    {
      Authorization: `Bearer ${token}`,
    },
  );

  return json(response);
};

export const DELETE: RequestHandler = async ({ request, locals }) => {
  const { id } = await request.json();
  const token = locals.token;

  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await delete_<string, string>(
    Urls.deleteIssue.replace("$$issue_id$$", id),
    {
      Authorization: `Bearer ${token}`,
    },
  );

  return json(response);
};
