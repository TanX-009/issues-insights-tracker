import { json, type RequestHandler } from "@sveltejs/kit";
import { post } from "$lib/api/config";
import Urls from "$lib/api/urls";
import { SECURE_COOKIES } from "$env/static/private";
import type { TUser } from "$lib/types/user";

interface TLoginResponse {
  access_token: string;
  token_type: "bearer";
  user: TUser;
}

interface TLoginRequest {
  grant_type: "password";
  username: string;
  password: string;
  scope: "";
  client_id: "";
  client_secret: "";
}

export const POST: RequestHandler = async ({ request, cookies }) => {
  const { email, password } = await request.json();

  const response = await post<TLoginRequest, TLoginResponse, "">(
    Urls.login,
    {
      grant_type: "password",
      scope: "",
      client_id: "",
      client_secret: "",
      username: email,
      password,
    },
    {
      contentType: "application/x-www-form-urlencoded",
    },
  );

  if (!response.success && response.status === 401) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  if (!response.success) {
    return json({ error: response.error }, { status: response.status });
  }

  cookies.set("auth_token", response.data.access_token, {
    httpOnly: true,
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 1 week
    sameSite: "lax",
    secure: SECURE_COOKIES == "true", // set to true in production
  });
  cookies.set("auth", JSON.stringify(response.data.user), {
    httpOnly: true,
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 1 week
    sameSite: "lax",
    secure: SECURE_COOKIES == "true", // set to true in production
  });

  return json(response.data);
};
