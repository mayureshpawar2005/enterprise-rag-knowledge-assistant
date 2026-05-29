import {
  Activity,
  BookOpen,
  Database,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
  Sun,
  Upload,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { HealthResponse } from "@/types/api";
import { cn } from "@/lib/utils";

interface HeaderProps {
  health: HealthResponse | null;
  isDark: boolean;
  onToggleTheme: () => void;
  activeView: "chat" | "upload";
  onViewChange: (view: "chat" | "upload") => void;
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  onToggleSources: () => void;
  sourcesOpen: boolean;
}

export function Header({
  health,
  isDark,
  onToggleTheme,
  activeView,
  onViewChange,
  onToggleSidebar,
  sidebarOpen,
  onToggleSources,
  sourcesOpen,
}: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center justify-between border-b border-border bg-background/80 px-4 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="lg:hidden" onClick={onToggleSidebar}>
          {sidebarOpen ? <PanelLeftClose /> : <PanelLeftOpen />}
        </Button>
        <div className="flex items-center gap-2">
          <div className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Sparkles className="size-4" />
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-semibold leading-none">Enterprise RAG</p>
            <p className="text-xs text-muted-foreground">Knowledge Assistant</p>
          </div>
        </div>
      </div>

      <nav className="flex items-center gap-1 rounded-lg bg-muted/60 p-1">
        <Button
          variant={activeView === "chat" ? "secondary" : "ghost"}
          size="sm"
          onClick={() => onViewChange("chat")}
          className="gap-1.5"
        >
          <BookOpen className="size-3.5" />
          Chat
        </Button>
        <Button
          variant={activeView === "upload" ? "secondary" : "ghost"}
          size="sm"
          onClick={() => onViewChange("upload")}
          className="gap-1.5"
        >
          <Upload className="size-3.5" />
          Upload
        </Button>
      </nav>

      <div className="flex items-center gap-2">
        {health && (
          <div className="hidden items-center gap-2 md:flex">
            <Badge variant={health.status === "healthy" ? "success" : "warning"}>
              <Activity className="mr-1 size-3" />
              {health.status}
            </Badge>
            <Badge variant="outline" className="gap-1">
              <Database className="size-3" />
              {health.documents_indexed} chunks
            </Badge>
          </div>
        )}
        <Button
          variant="outline"
          size="sm"
          className="hidden md:inline-flex"
          onClick={onToggleSources}
        >
          {sourcesOpen ? "Hide sources" : "Show sources"}
        </Button>
        <Button variant="ghost" size="icon" onClick={onToggleTheme} aria-label="Toggle theme">
          {isDark ? <Sun /> : <Moon />}
        </Button>
      </div>
    </header>
  );
}

export function StatCards({ health }: { health: HealthResponse | null }) {
  const stats = [
    {
      label: "System status",
      value: health?.status ?? "—",
      hint: health?.gemini_configured ? "Gemini connected" : "Gemini not configured",
    },
    {
      label: "Indexed chunks",
      value: health?.documents_indexed?.toString() ?? "—",
      hint: "In ChromaDB vector store",
    },
    {
      label: "ChromaDB",
      value: health?.chroma_connected ? "Connected" : "Offline",
      hint: "Vector database",
    },
    {
      label: "API version",
      value: health?.version ?? "—",
      hint: "FastAPI backend",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={cn(
            "rounded-xl border border-border bg-card p-4 shadow-sm transition-colors",
            "hover:border-primary/30"
          )}
        >
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {stat.label}
          </p>
          <p className="mt-2 text-2xl font-semibold capitalize">{stat.value}</p>
          <p className="mt-1 text-xs text-muted-foreground">{stat.hint}</p>
        </div>
      ))}
    </div>
  );
}
