import type {
  AskRequest,
  AskResponse,
  HealthResponse,
  UploadResponse,
} from "@/types/api";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export async function uploadPdfs(files: File[]): Promise<UploadResponse[]> {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  const data = await response.json();
  return Array.isArray(data) ? data : [data];
}

export async function askQuestion(payload: AskRequest): Promise<AskResponse> {
  return request<AskResponse>("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
