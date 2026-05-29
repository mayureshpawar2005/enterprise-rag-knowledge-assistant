import { useCallback, useState } from "react";
import { CheckCircle2, FileText, Loader2, UploadCloud, X } from "lucide-react";
import { uploadPdfs } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { UploadResponse } from "@/types/api";

interface FileUploadZoneProps {
  onUploadComplete?: () => void;
}

export function FileUploadZone({ onUploadComplete }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<UploadResponse[]>([]);
  const [queue, setQueue] = useState<File[]>([]);

  const handleFiles = useCallback((files: FileList | File[]) => {
    const pdfs = Array.from(files).filter(
      (f) => f.type === "application/pdf" || f.name.toLowerCase().endsWith(".pdf")
    );
    if (pdfs.length === 0) {
      setError("Please select valid PDF files.");
      return;
    }
    setError(null);
    setQueue((prev) => [...prev, ...pdfs]);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const uploadAll = async () => {
    if (queue.length === 0 || isUploading) return;
    setIsUploading(true);
    setError(null);
    try {
      const uploaded = await uploadPdfs(queue);
      setResults((prev) => [...uploaded, ...prev]);
      setQueue([]);
      onUploadComplete?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const removeFromQueue = (index: number) => {
    setQueue((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Upload documents</CardTitle>
          <CardDescription>
            Drag and drop PDF files or browse to index them in ChromaDB for Q&amp;A.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            className={cn(
              "relative flex min-h-[220px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 transition-all",
              isDragging
                ? "border-primary bg-primary/5 scale-[1.01]"
                : "border-border hover:border-primary/50 hover:bg-muted/30"
            )}
          >
            <input
              type="file"
              accept=".pdf,application/pdf"
              multiple
              className="absolute inset-0 cursor-pointer opacity-0"
              onChange={(e) => e.target.files && handleFiles(e.target.files)}
            />
            <div
              className={cn(
                "mb-4 flex size-14 items-center justify-center rounded-full bg-primary/10 text-primary transition-transform",
                isDragging && "scale-110"
              )}
            >
              <UploadCloud className="size-7" />
            </div>
            <p className="text-base font-medium">Drop PDFs here</p>
            <p className="mt-1 text-sm text-muted-foreground">or click to browse — multiple files supported</p>
          </div>

          {queue.length > 0 && (
            <div className="space-y-2 rounded-xl border border-border bg-muted/20 p-4">
              <p className="text-sm font-medium">{queue.length} file(s) ready</p>
              <ul className="space-y-2">
                {queue.map((file, i) => (
                  <li
                    key={`${file.name}-${i}`}
                    className="flex items-center justify-between rounded-lg bg-background px-3 py-2 text-sm"
                  >
                    <span className="flex items-center gap-2 truncate">
                      <FileText className="size-4 shrink-0 text-primary" />
                      {file.name}
                    </span>
                    <Button variant="ghost" size="icon" className="size-7" onClick={() => removeFromQueue(i)}>
                      <X className="size-3.5" />
                    </Button>
                  </li>
                ))}
              </ul>
              <Button onClick={uploadAll} disabled={isUploading} className="w-full">
                {isUploading ? (
                  <>
                    <Loader2 className="animate-spin" />
                    Indexing documents…
                  </>
                ) : (
                  <>
                    <UploadCloud />
                    Upload &amp; index
                  </>
                )}
              </Button>
            </div>
          )}

          {error && (
            <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          )}
        </CardContent>
      </Card>

      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent uploads</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {results.map((r) => (
              <div
                key={r.document_id}
                className="flex items-start gap-3 rounded-lg border border-border bg-background p-3 animate-fade-in"
              >
                <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-500" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{r.filename}</p>
                  <p className="text-xs text-muted-foreground">
                    {r.chunks_indexed} chunks indexed · {r.total_documents_in_store} total in store
                  </p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
