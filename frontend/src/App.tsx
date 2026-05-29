import { useState } from "react";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { Header, StatCards } from "@/components/layout/Header";
import { ChatSidebar } from "@/components/layout/ChatSidebar";
import { SourcesPanel } from "@/components/sources/SourcesPanel";
import { FileUploadZone } from "@/components/upload/FileUploadZone";
import { useChatStore } from "@/hooks/useChatStore";
import { useTheme } from "@/hooks/useTheme";
import { cn } from "@/lib/utils";

export default function App() {
  const { theme, toggleTheme, isDark } = useTheme();
  const {
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
  } = useChatStore();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sourcesOpen, setSourcesOpen] = useState(true);
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);

  const handleShowSources = (messageId: string) => {
    const message = activeSession?.messages.find((m) => m.id === messageId);
    if (message?.sources) {
      setSelectedSources(message.sources);
      setSelectedMessageId(messageId);
      setSourcesOpen(true);
    }
  };

  const showMobileOverlay = sidebarOpen;

  return (
    <div className={cn("flex h-dvh flex-col", theme === "dark" && "dark")}>
      <Header
        health={health}
        isDark={isDark}
        onToggleTheme={toggleTheme}
        activeView={activeView}
        onViewChange={setActiveView}
        onToggleSidebar={() => setSidebarOpen((v) => !v)}
        sidebarOpen={sidebarOpen}
        onToggleSources={() => setSourcesOpen((v) => !v)}
        sourcesOpen={sourcesOpen}
      />

      <div className="relative flex min-h-0 flex-1">
        {/* Sidebar — desktop always visible, mobile overlay */}
        <div
          className={cn(
            "fixed inset-y-14 left-0 z-20 w-72 -translate-x-full transition-transform lg:static lg:z-0 lg:translate-x-0 lg:pt-0",
            (sidebarOpen || showMobileOverlay) && "translate-x-0",
            "top-14 lg:top-0"
          )}
        >
          <ChatSidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onNewChat={() => {
              startNewChat();
              setSidebarOpen(false);
            }}
            onSelectSession={(id) => {
              selectSession(id);
              setSidebarOpen(false);
            }}
            onDeleteSession={deleteSession}
            className="h-[calc(100dvh-3.5rem)] lg:h-full"
          />
        </div>

        {showMobileOverlay && (
          <button
            type="button"
            aria-label="Close sidebar"
            className="fixed inset-0 z-10 bg-black/40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main content */}
        <main className="flex min-w-0 flex-1 flex-col">
          {activeView === "upload" ? (
            <div className="flex-1 overflow-y-auto p-4 md:p-8">
              <div className="mx-auto mb-8 w-full max-w-5xl">
                <h1 className="text-2xl font-bold tracking-tight">Document upload</h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  Index PDFs into the enterprise knowledge base.
                </p>
                <div className="mt-6">
                  <StatCards health={health} />
                </div>
              </div>
              <FileUploadZone onUploadComplete={refreshHealth} />
            </div>
          ) : (
            <ChatInterface
              session={activeSession}
              isLoading={isLoading}
              error={error}
              onSend={sendMessage}
              onShowSources={handleShowSources}
              selectedMessageId={selectedMessageId}
            />
          )}
        </main>

        {/* Sources panel — desktop sidebar, mobile full overlay when open */}
        {activeView === "chat" && sourcesOpen && (
          <>
            <div className="hidden w-80 shrink-0 xl:block">
              <SourcesPanel sources={selectedSources} />
            </div>
            <div className="fixed inset-y-14 right-0 z-20 w-full max-w-md border-l border-border bg-background shadow-xl xl:hidden">
              <SourcesPanel
                sources={selectedSources}
                onClose={() => setSourcesOpen(false)}
                className="h-full"
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
