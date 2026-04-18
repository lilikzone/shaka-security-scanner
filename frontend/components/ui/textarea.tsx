import * as React from "react";
import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "min-h-[100px] w-full rounded-lg border border-border bg-panelAlt px-3 py-2 text-sm text-foreground placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60",
        className
      )}
      {...props}
    />
  )
);

Textarea.displayName = "Textarea";
