import { json, type RequestHandler } from "@sveltejs/kit";
import { get, post, put, delete_ } from "$lib/api/config";
import Urls from "$lib/api/urls";
import type { TUser } from "$lib/types/user";

interface TCreateUserRequest {
  email: string;
  role: TUser["role"];
  password: string;
}

interface TUpdateUserRequest {
  id: TUser["id"];
  email: string;
  role: TUser["role"];
  password: string;
}

interface TDeleteUserRequest {
  id: TUser["id"];
}

export const GET: RequestHandler = async ({ locals }) => {
  const token = locals.token;
  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await get<TUser[], "">(Urls.getUsers, {
    Authorization: `Bearer ${token}`,
  });

  return json(response);
};

export const POST: RequestHandler = async ({ request, locals }) => {
  const token = locals.token;
  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as TCreateUserRequest;

  const response = await post<TCreateUserRequest, TUser, "">(
    Urls.createUser,
    body,
    {
      Authorization: `Bearer ${token}`,
    },
  );

  return json(response);
};

export const PUT: RequestHandler = async ({ request, locals }) => {
  const token = locals.token;
  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = (await request.json()) as TUpdateUserRequest;

  const response = await put<TUpdateUserRequest, TUser, "">(
    Urls.updateUser.replace("$$user_id$$", String(body.id)),
    {
      email: body.email,
      role: body.role,
      password: body.password,
      id: body.id,
    },
    {
      Authorization: `Bearer ${token}`,
    },
  );

  return json(response);
};

export const DELETE: RequestHandler = async ({ request, locals }) => {
  const token = locals.token;
  if (!token) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  const { id } = (await request.json()) as TDeleteUserRequest;

  const response = await delete_<string, string>(
    Urls.deleteUser.replace("$$user_id$$", String(id)),
    {
      Authorization: `Bearer ${token}`,
    },
  );

  return json(response);
};
