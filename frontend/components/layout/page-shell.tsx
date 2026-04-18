import { PropsWithChildren } from "react";
import { AppSidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";

export function PageShell({ children }: PropsWithChildren) {
  return (
    <div className="flex min-h-screen">
      <AppSidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="flex-1 p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
