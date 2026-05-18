export type AskLimit = 3 | 5 | 10;

export interface HealthResponse {
  status: string;
  database?: string;
}

export interface RagSource {
  document_id: number;
  document_type: string;
  document_number: string | null;
  status: string | null;
  product_full_name: string | null;
  final_score: number | null;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: RagSource[];
}

export class ApiClientError extends Error {
  kind: "network" | "backend";
  status?: number;

  constructor(message: string, kind: "network" | "backend", status?: number) {
    super(message);
    this.name = "ApiClientError";
    this.kind = kind;
    this.status = status;
  }
}
