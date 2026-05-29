export interface SourceChunk {
  content: string;
  document_name: string;
  chunk_index: number;
  page: number | null;
  relevance_score: number;
  citation: string;
}

export interface UploadResponse {
  message: string;
  filename: string;
  document_id: string;
  chunks_indexed: number;
  total_documents_in_store: number;
}

export interface AskRequest {
  question: string;
  session_id?: string;
  top_k?: number;
}

export interface AskResponse {
  answer: string;
  sources: SourceChunk[];
  session_id: string | null;
  question: string;
  fallback_mode: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  chroma_connected: boolean;
  gemini_configured: boolean;
  documents_indexed: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceChunk[];
  fallbackMode?: boolean;
  timestamp: number;
}

export interface ChatSession {
  id: string;
  backendSessionId?: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  updatedAt: number;
}
