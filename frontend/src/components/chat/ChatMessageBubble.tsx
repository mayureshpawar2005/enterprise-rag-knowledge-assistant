import { AlertTriangle, Bot, FileSearch, User } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { ChatMessage } from "@/types/api";
import { cn } from "@/lib/utils";

interface ChatMessageBubbleProps {
  message: ChatMessage;
  onShowSources?: () => void;
  isSelected?: boolean;
}

export function ChatMessageBubble({
  message,
  onShowSources,
  isSelected,
}: ChatMessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "animate-fade-in flex gap-3 px-4 py-3",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Bot className="size-4" />
        </div>
      )}

      <div className={cn("flex max-w-[85%] flex-col gap-2", isUser && "items-end")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm",
            isUser
              ? "rounded-br-md bg-primary text-primary-foreground"
              : "rounded-bl-md border border-border bg-card"
          )}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>

        {!isUser && (
          <div className="flex flex-wrap items-center gap-2">
            {message.fallbackMode && (
              <Badge variant="warning" className="gap-1">
                <AlertTriangle className="size-3" />
                Quota fallback
              </Badge>
            )}
            {message.sources && message.sources.length > 0 && (
              <button
                type="button"
                onClick={onShowSources}
                className={cn(
                  "inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
                  isSelected && "bg-accent text-accent-foreground"
                )}
              >
                <FileSearch className="size-3" />
                {message.sources.length} source{message.sources.length !== 1 ? "s" : ""}
              </button>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
          <User className="size-4" />
        </div>
      )}
    </div>
  );
}
