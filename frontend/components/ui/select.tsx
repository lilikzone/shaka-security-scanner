import * as React from "react";
import { cn } from "@/lib/utils";

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  options: Array<{ label: string; value: string }>;
}

export function Select({ className, options, ...props }: SelectProps) {
  return (
    <select
      className={cn(
        "h-10 w-full rounded-lg border border-border bg-panelAlt px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60",
        className
      )}
      {...props}
    >
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
