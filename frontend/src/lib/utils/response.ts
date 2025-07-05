import type { TApiResponse, TErrorResponse } from "$lib/api/config";

export default function handleResponse<TResponse>(
  response: TApiResponse<TResponse>,
  onSuccess: (res: TResponse) => void,
  onError: (err: TErrorResponse) => void,
): number {
  if (!response.success) {
    onError(response.error);
  }

  if (response.success) onSuccess(response.data);
  return response.status;
}
