import { json, type RequestHandler } from "@sveltejs/kit";
import { post } from "$lib/api/config";
import Urls from "$lib/api/urls";
import handleResponse from "$lib/utils/response";
import { SECURE_COOKIES } from "$env/static/private";

interface TLoginResponse {
  access_token: string;
  token_type: "bearer";
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

  return handleResponse(response, (res) => {
    cookies.set("auth_token", res.access_token, {
      httpOnly: true,
      path: "/",
      maxAge: 60 * 60 * 24 * 7, // 1 week
      sameSite: "lax",
      secure: SECURE_COOKIES == "true", // set to true in production
    });
  });
};
