import { cn } from "@/lib/utils";
import * as React from "react";

export function Table({ children, className }: React.PropsWithChildren<{ className?: string }>) {
  return <table className={cn("w-full border-collapse text-left", className)}>{children}</table>;
}

export function THead({ children }: React.PropsWithChildren) {
  return <thead className="bg-panelAlt/80 text-xs uppercase tracking-wide text-slate-300">{children}</thead>;
}

export function TBody({ children }: React.PropsWithChildren) {
  return <tbody className="divide-y divide-border">{children}</tbody>;
}

export function TR({ children, className, ...props }: React.PropsWithChildren<React.HTMLAttributes<HTMLTableRowElement>>) {
  return (
    <tr className={cn("transition-colors hover:bg-panelAlt/40", className)} {...props}>
      {children}
    </tr>
  );
}

export function TH({ children, className, ...props }: React.PropsWithChildren<React.ThHTMLAttributes<HTMLTableCellElement>>) {
  return (
    <th className={cn("px-4 py-3 font-medium", className)} {...props}>
      {children}
    </th>
  );
}

export function TD({ children, className, ...props }: React.PropsWithChildren<React.TdHTMLAttributes<HTMLTableCellElement>>) {
  return (
    <td className={cn("px-4 py-3 text-sm text-slate-200", className)} {...props}>
      {children}
    </td>
  );
}
