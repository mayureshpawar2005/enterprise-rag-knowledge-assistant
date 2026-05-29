import { useCallback, useEffect, useState } from "react";
import { askQuestion, fetchHealth } from "@/lib/api";
import type { ChatMessage, ChatSession, HealthResponse, SourceChunk } from "@/types/api";

const STORAGE_KEY = "enterprise-rag-sessions";
const ACTIVE_KEY = "enterprise-rag-active-session";

function createId() {
  return crypto.randomUUID();
}

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ChatSession[]) : [];
  } catch {
    return [];
  }
}

function saveSessions(sessions: ChatSession[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

function createSession(title = "New conversation"): ChatSession {
  const now = Date.now();
  return {
    id: createId(),
    title,
    messages: [],
    createdAt: now,
    updatedAt: now,
  };
}

export function useChatStore() {
  const [sessions, setSessions] = useState<ChatSession[]>(() => loadSessions());
  const [activeSessionId, setActiveSessionId] = useState<string | null>(() => {
    const stored = localStorage.getItem(ACTIVE_KEY);
    const loaded = loadSessions();
    if (stored && loaded.some((s) => s.id === stored)) return stored;
    return loaded[0]?.id ?? null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [selectedSources, setSelectedSources] = useState<SourceChunk[]>([]);
  const [activeView, setActiveView] = useState<"chat" | "upload">("chat");

  const activeSession = sessions.find((s) => s.id === activeSessionId) ?? null;

  useEffect(() => {
    saveSessions(sessions);
  }, [sessions]);

  useEffect(() => {
    if (activeSessionId) localStorage.setItem(ACTIVE_KEY, activeSessionId);
  }, [activeSessionId]);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const refreshHealth = useCallback(async () => {
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch {
      setHealth(null);
    }
  }, []);

  const startNewChat = useCallback(() => {
    const session = createSession();
    setSessions((prev) => [session, ...prev]);
    setActiveSessionId(session.id);
    setSelectedSources([]);
    setActiveView("chat");
    setError(null);
  }, []);

  const selectSession = useCallback((id: string) => {
    setActiveSessionId(id);
    setSelectedSources([]);
    setActiveView("chat");
    setError(null);
  }, []);

  const deleteSession = useCallback(
    (id: string) => {
      setSessions((prev) => {
        const next = prev.filter((s) => s.id !== id);
        if (activeSessionId === id) {
          setActiveSessionId(next[0]?.id ?? null);
        }
        return next;
      });
    },
    [activeSessionId]
  );

  const sendMessage = useCallback(
    async (question: string) => {
      if (!question.trim() || isLoading) return;

      let sessionId = activeSessionId;
      let session = sessions.find((s) => s.id === sessionId);

      if (!session) {
        session = createSession(question.slice(0, 48));
        sessionId = session.id;
        setSessions((prev) => [session!, ...prev]);
        setActiveSessionId(sessionId);
      }

      const userMessage: ChatMessage = {
        id: createId(),
        role: "user",
        content: question.trim(),
        timestamp: Date.now(),
      };

      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId
            ? {
                ...s,
                title: s.messages.length === 0 ? truncateTitle(question) : s.title,
                messages: [...s.messages, userMessage],
                updatedAt: Date.now(),
              }
            : s
        )
      );
      setIsLoading(true);
      setError(null);
      setSelectedSources([]);

      try {
        const response = await askQuestion({
          question: question.trim(),
          session_id: session.backendSessionId,
        });

        const assistantMessage: ChatMessage = {
          id: createId(),
          role: "assistant",
          content: response.answer,
          sources: response.sources,
          fallbackMode: response.fallback_mode,
          timestamp: Date.now(),
        };

        setSessions((prev) =>
          prev.map((s) =>
            s.id === sessionId
              ? {
                  ...s,
                  backendSessionId: response.session_id ?? s.backendSessionId,
                  messages: [...s.messages, assistantMessage],
                  updatedAt: Date.now(),
                }
              : s
          )
        );
        setSelectedSources(response.sources);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to get answer";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [activeSessionId, isLoading, sessions]
  );

  return {
    sessions,
    activeSession,
    activeSessionId,
    isLoading,
    error,
    health,
    selectedSources,
    setSelectedSources,
    activeView,
    setActiveView,
    startNewChat,
    selectSession,
    deleteSession,
    sendMessage,
    refreshHealth,
  };
}

function truncateTitle(text: string): string {
  const t = text.trim();
  return t.length > 42 ? `${t.slice(0, 42)}…` : t;
}
