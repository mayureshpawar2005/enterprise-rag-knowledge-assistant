import { useEffect, useRef, useState } from "react";
import { ArrowUp, Sparkles } from "lucide-react";
import { ChatMessageBubble } from "@/components/chat/ChatMessageBubble";
import { Button } from "@/components/ui/button";
import { LoadingDots } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/input";
import type { ChatSession } from "@/types/api";

interface ChatInterfaceProps {
  session: ChatSession | null;
  isLoading: boolean;
  error: string | null;
  onSend: (message: string) => void;
  onShowSources: (messageId: string) => void;
  selectedMessageId: string | null;
}

export function ChatInterface({
  session,
  isLoading,
  error,
  onSend,
  onShowSources,
  selectedMessageId,
}: ChatInterfaceProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [session?.messages, isLoading]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const messages = session?.messages ?? [];

  return (
    <div className="flex h-full min-h-0 flex-1 flex-col">
      <ScrollArea className="flex-1">
        <div className="mx-auto w-full max-w-3xl py-6">
          {messages.length === 0 && !isLoading && (
            <div className="flex flex-col items-center justify-center px-6 py-20 text-center">
              <div className="mb-4 flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <Sparkles className="size-7" />
              </div>
              <h2 className="text-xl font-semibold">Ask your documents anything</h2>
              <p className="mt-2 max-w-md text-sm text-muted-foreground">
                Upload PDFs in the Upload tab, then ask questions here. Answers include
                source citations from your indexed knowledge base.
              </p>
              <div className="mt-8 grid w-full max-w-lg gap-2 sm:grid-cols-2">
                {[
                  "What are the key findings in the report?",
                  "Summarize the main risks mentioned.",
                  "What policies apply to data retention?",
                  "List action items from the document.",
                ].map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => setInput(prompt)}
                    className="rounded-xl border border-border bg-card px-3 py-2.5 text-left text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:bg-accent hover:text-foreground"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessageBubble
              key={message.id}
              message={message}
              isSelected={selectedMessageId === message.id}
              onShowSources={() => onShowSources(message.id)}
            />
          ))}

          {isLoading && (
            <div className="flex items-center gap-3 px-4 py-4 animate-fade-in">
              <div className="flex size-8 items-center justify-center rounded-lg bg-primary/10">
                <Sparkles className="size-4 text-primary" />
              </div>
              <div className="rounded-2xl rounded-bl-md border border-border bg-card px-4 py-3">
                <LoadingDots />
              </div>
            </div>
          )}

          {error && (
            <div className="mx-4 mb-4 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <div className="shrink-0 border-t border-border bg-background/80 p-4 backdrop-blur-md">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-border bg-card p-2 shadow-sm focus-within:ring-2 focus-within:ring-ring"
        >
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Ask a question about your documents…"
            rows={1}
            disabled={isLoading}
            className="min-h-[44px] flex-1 border-0 bg-transparent shadow-none focus-visible:ring-0"
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading}
            className="shrink-0 rounded-xl"
            aria-label="Send message"
          >
            <ArrowUp />
          </Button>
        </form>
        <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-muted-foreground">
          Answers are generated from uploaded PDFs using RAG + Gemini.
        </p>
      </div>
    </div>
  );
}
