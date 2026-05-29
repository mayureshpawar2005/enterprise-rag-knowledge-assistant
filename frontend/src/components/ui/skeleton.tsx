import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-shimmer rounded-md bg-muted", className)}
      {...props}
    />
  );
}

export function LoadingDots({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-1.5", className)}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="size-2 rounded-full bg-primary animate-pulse-dot"
          style={{ animationDelay: `${i * 0.16}s` }}
        />
      ))}
    </div>
  );
}
