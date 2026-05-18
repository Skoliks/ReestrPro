import {
  ApiClientError,
  type AskResponse,
  type HealthResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseErrorPayload(response: Response): Promise<string | null> {
  const contentType = response.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    const payload = (await response.json()) as { detail?: unknown };

    if (typeof payload.detail === "string") {
      return payload.detail;
    }

    if (payload.detail) {
      return JSON.stringify(payload.detail);
    }

    return null;
  }

  const text = await response.text();
  return text || null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });

    if (!response.ok) {
      const message = await parseErrorPayload(response);

      throw new ApiClientError(
        message ?? `Backend returned ${response.status}`,
        "backend",
        response.status,
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }

    throw new ApiClientError("Network request failed", "network");
  }
}

export function getHealth() {
  return request<HealthResponse>("/health", {
    method: "GET",
  });
}

export function askQuestion(question: string, limit: number) {
  return request<AskResponse>("/ask", {
    method: "POST",
    body: JSON.stringify({
      question,
      limit,
    }),
  });
}
