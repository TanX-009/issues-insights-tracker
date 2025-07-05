import { PUBLIC_API_URL } from "$env/static/public";
import axios, { type AxiosRequestConfig } from "axios";
// import Services from "./serviceUrls";

interface TErrorResponse {
  detail: string;
  [key: string]: string | string[] | number | boolean | undefined;
}

interface TApiSuccess<T> {
  success: true;
  status: 200;
  data: T;
}

interface TApiFailure {
  success: false;
  status: number;
  error: TErrorResponse;
}

type TApiResponse<T> = TApiSuccess<T> | TApiFailure;

const instance = axios.create({
  baseURL: PUBLIC_API_URL,
  timeout: 300000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

// async function handleTokenRefresh<TResponse>(
//   originalRequest: AxiosRequestConfig,
// ): Promise<TApiResponse<TResponse>> {
//   // retry the original request
//   return await axios<TResponse>(originalRequest)
//     .then(
//       (retryResponse) =>
//         // return the retired request data
//         ({
//           success: true,
//           data: retryResponse.data,
//         }) as TApiResponse<TResponse>,
//     )
//     .catch((retryError) => {
//       console.error("Retry failed: ", retryError);
//       return {
//         success: false,
//         status: retryError.status,
//         error: { detail: "Retry failed!", error: retryError },
//       };
//     });
// }
//
// async function handle401Error<TResponse>(
//   originalRequest: AxiosRequestConfig,
// ): Promise<TApiResponse<TResponse>> {
//   try {
//     // try to refresh token
//     await instance.post<TResponse>(
//       Services.refresh,
//       {},
//       { withCredentials: true },
//     );
//
//     // if refreshed successfully
//     return await handleTokenRefresh(originalRequest);
//   } catch (error) {
//     // the tokens are now expired
//     console.error("Refresh token error: ", error);
//     // ------------------------------------------
//     // delete tokens from user and logout the user
//     //
//     // handler block when the tokens expire
//     // ------------------------------------------
//     return {
//       success: false,
//       status: 401,
//       error: {
//         detail: "Refresh token expired!",
//         error: error,
//       } as TErrorResponse,
//     };
//   }
// }

async function requestFailureCallback<TResponse>(
  error: unknown,
): Promise<TApiResponse<TResponse>> {
  if (!axios.isAxiosError(error)) {
    // error is unknown and unexpected
    console.error("Error: ", error);
    return {
      success: false,
      status: 0,
      error: { detail: "An unexpected error occurred!" } as TErrorResponse,
    };
  }

  if (error.code === "ERR_NETWORK") {
    return {
      success: false,
      status: 0,
      error: { detail: "Network error!" },
    };
  }

  if (!error.response) {
    return {
      success: false,
      status: 0,
      error: { detail: "Unknown network error occured!" },
    };
  }

  const originalRequest = error.config as AxiosRequestConfig;

  if (!originalRequest) {
    console.error("Original request config not found!");
    return {
      success: false,
      status: error.response.status,
      error: { detail: "An unexpected error occurred!" },
    };
  }

  if (error.response.status === 401) {
    return {
      success: false,
      status: 401,
      error: {
        detail: "Token expired!",
        data: error.response.data,
      },
    };
    // return await handle401Error<TResponse>(originalRequest);
  }

  // other error by server
  return {
    success: false,
    status: error.response.status,
    error: {
      detail: "Request failed with status: " + error.response.status,
      data: error.response.data,
    },
  };
}

async function get<TResponse, TRequestParams>(
  url: string,
  options: {
    params?: TRequestParams;
    withCredentials?: boolean;
    Authorization?: string;
    contentType?:
      | "application/json"
      | "multipart/form-data"
      | "application/x-www-form-urlencoded";
  } = {
    contentType: "application/json",
    Authorization: "",
  },
): Promise<TApiResponse<TResponse>> {
  try {
    const response = await instance.get<TResponse>(url, {
      params: options?.params ?? {},
      withCredentials: options?.withCredentials ?? false,
      headers: {
        "Content-Type": options.contentType,
        Authorization: options.Authorization,
      },
    });
    return { success: true, status: 200, data: response.data };
  } catch (error) {
    return requestFailureCallback(error);
  }
}

async function put<TRequest, TResponse, TRequestParams>(
  url: string,
  data: TRequest,
  options: {
    params?: TRequestParams;
    withCredentials?: boolean;
    Authorization?: string;
    contentType?:
      | "application/json"
      | "multipart/form-data"
      | "application/x-www-form-urlencoded";
  } = {
    contentType: "application/json",
    Authorization: "",
  },
): Promise<TApiResponse<TResponse>> {
  try {
    const response = await instance.put<TResponse>(url, data, {
      params: options?.params ?? {},
      withCredentials: options?.withCredentials ?? false,
      headers: {
        "Content-Type": options.contentType,
        Authorization: options.Authorization,
      },
    });
    return { success: true, status: 200, data: response.data };
  } catch (error) {
    return requestFailureCallback(error);
  }
}

async function patch<TRequest, TResponse, TRequestParams>(
  url: string,
  data: TRequest,
  options: {
    params?: TRequestParams;
    withCredentials?: boolean;
    Authorization?: string;
    contentType?:
      | "application/json"
      | "multipart/form-data"
      | "application/x-www-form-urlencoded";
  } = {
    contentType: "application/json",
    Authorization: "",
  },
): Promise<TApiResponse<TResponse>> {
  try {
    const response = await instance.patch<TResponse>(url, data, {
      params: options?.params ?? {},
      withCredentials: options?.withCredentials ?? false,
      headers: {
        "Content-Type": options.contentType,
        Authorization: options.Authorization,
      },
    });
    return { success: true, status: 200, data: response.data };
  } catch (error) {
    return requestFailureCallback(error);
  }
}

async function post<TRequest, TResponse, TRequestParams>(
  url: string,
  data: TRequest,
  options: {
    params?: TRequestParams;
    withCredentials?: boolean;
    Authorization?: string;
    contentType?:
      | "application/json"
      | "multipart/form-data"
      | "application/x-www-form-urlencoded";
  } = {
    contentType: "application/json",
    Authorization: "",
  },
): Promise<TApiResponse<TResponse>> {
  try {
    const response = await instance.post<TResponse>(url, data, {
      params: options?.params ?? {},
      withCredentials: options?.withCredentials ?? false,
      headers: {
        "Content-Type": options.contentType,
        Authorization: options.Authorization,
      },
    });
    return { success: true, status: 200, data: response.data };
  } catch (error) {
    return requestFailureCallback(error);
  }
}

async function delete_<TRequestParams, TResponse>(
  url: string,
  options: {
    params?: TRequestParams;
    withCredentials?: boolean;
    Authorization?: string;
    contentType?:
      | "application/json"
      | "multipart/form-data"
      | "application/x-www-form-urlencoded";
  } = {
    contentType: "application/json",
    Authorization: "",
  },
): Promise<TApiResponse<TResponse>> {
  try {
    const response = await instance.delete<TResponse>(url, {
      params: options?.params ?? {},
      withCredentials: options?.withCredentials ?? false,
      headers: {
        "Content-Type": options.contentType,
        Authorization: options.Authorization,
      },
    });
    return { success: true, status: 200, data: response.data };
  } catch (error) {
    return requestFailureCallback(error);
  }
}

export { get, put, patch, post, delete_ };

export type { TApiResponse, TErrorResponse };
