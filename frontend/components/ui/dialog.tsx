import { PropsWithChildren } from "react";
import { cn } from "@/lib/utils";

interface DialogProps extends PropsWithChildren {
  open: boolean;
  onClose: () => void;
  title: string;
}

export function Dialog({ open, onClose, title, children }: DialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
      <div className="absolute inset-0" onClick={onClose} />
      <div className={cn("relative z-10 w-full max-w-2xl rounded-xl border border-border bg-panel p-6 shadow-2xl")}>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
          <button onClick={onClose} className="text-sm text-slate-400 hover:text-slate-200">
            Close
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
