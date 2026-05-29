import { MessageSquarePlus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import type { ChatSession } from "@/types/api";
import { cn, formatRelativeTime } from "@/lib/utils";

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onNewChat: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  className?: string;
}

export function ChatSidebar({
  sessions,
  activeSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  className,
}: ChatSidebarProps) {
  return (
    <aside
      className={cn(
        "flex h-full w-full flex-col border-r border-border bg-card/50",
        className
      )}
    >
      <div className="p-3">
        <Button onClick={onNewChat} className="w-full justify-start gap-2" size="sm">
          <MessageSquarePlus className="size-4" />
          New chat
        </Button>
      </div>
      <Separator />
      <ScrollArea className="flex-1 px-2 py-2">
        <div className="space-y-1">
          {sessions.length === 0 && (
            <p className="px-2 py-6 text-center text-xs text-muted-foreground">
              No conversations yet. Start a new chat or upload PDFs.
            </p>
          )}
          {sessions.map((session) => (
            <div
              key={session.id}
              className={cn(
                "group flex items-center gap-1 rounded-lg transition-colors",
                activeSessionId === session.id ? "bg-accent" : "hover:bg-muted/70"
              )}
            >
              <button
                type="button"
                onClick={() => onSelectSession(session.id)}
                className="flex min-w-0 flex-1 flex-col items-start px-3 py-2.5 text-left"
              >
                <span className="w-full truncate text-sm font-medium">{session.title}</span>
                <span className="text-xs text-muted-foreground">
                  {formatRelativeTime(session.updatedAt)}
                </span>
              </button>
              <Button
                variant="ghost"
                size="icon"
                className="mr-1 size-7 shrink-0 opacity-0 group-hover:opacity-100"
                onClick={() => onDeleteSession(session.id)}
                aria-label="Delete conversation"
              >
                <Trash2 className="size-3.5" />
              </Button>
            </div>
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}
