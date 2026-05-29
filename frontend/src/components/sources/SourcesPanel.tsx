import { BookMarked, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import type { SourceChunk } from "@/types/api";
import { cn } from "@/lib/utils";

interface SourcesPanelProps {
  sources: SourceChunk[];
  onClose?: () => void;
  className?: string;
}

export function SourcesPanel({ sources, onClose, className }: SourcesPanelProps) {
  return (
    <aside
      className={cn(
        "flex h-full w-full flex-col border-l border-border bg-card/50",
        className
      )}
    >
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <BookMarked className="size-4 text-primary" />
          <h2 className="text-sm font-semibold">Sources</h2>
          <Badge variant="secondary">{sources.length}</Badge>
        </div>
        {onClose && (
          <Button variant="ghost" size="icon" className="size-8" onClick={onClose}>
            <X className="size-4" />
          </Button>
        )}
      </div>
      <Separator />
      <ScrollArea className="flex-1">
        <div className="space-y-3 p-4">
          {sources.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">
              Source citations appear here after you ask a question.
            </p>
          )}
          {sources.map((source, index) => (
            <article
              key={`${source.citation}-${index}`}
              className="animate-fade-in rounded-xl border border-border bg-background p-4 shadow-sm"
            >
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <Badge variant="outline" className="font-mono text-[10px]">
                  #{index + 1}
                </Badge>
                <span className="text-xs font-medium text-primary">{source.document_name}</span>
                {source.page != null && (
                  <span className="text-xs text-muted-foreground">p. {source.page}</span>
                )}
              </div>
              <p className="mb-2 text-xs font-medium text-muted-foreground">{source.citation}</p>
              <p className="text-sm leading-relaxed text-foreground/90">{source.content}</p>
              <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                <span>Chunk {source.chunk_index}</span>
                <span>Relevance {(source.relevance_score * 100).toFixed(0)}%</span>
              </div>
            </article>
          ))}
        </div>
      </ScrollArea>
    </aside>
  );
}
