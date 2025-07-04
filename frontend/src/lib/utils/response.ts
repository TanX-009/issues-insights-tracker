import type { TApiResponse } from "$lib/api/config";
import { json } from "@sveltejs/kit";

export default async function handleResponse<TResponse>(
  response: TApiResponse<TResponse>,
  onSuccess?: (res: TResponse) => void | Promise<void>,
) {
  if (!response.success && response.status === 401) {
    return json({ error: "Unauthorized" }, { status: 401 });
  }

  if (!response.success) {
    return json({ error: response.error }, { status: response.status });
  }

  if (onSuccess) await onSuccess(response.data);

  return json(response.data);
}
