import { create } from "zustand";
import { AudienceMode } from "@/types/security";

interface UiState {
  audienceMode: AudienceMode;
  sidebarCollapsed: boolean;
  selectedVulnerabilityId?: string;
  scanCreationOpen: boolean;
  toggleAudienceMode: () => void;
  toggleSidebar: () => void;
  selectVulnerability: (id: string) => void;
  setScanCreationOpen: (open: boolean) => void;
}

export const useUiStore = create<UiState>((set) => ({
  audienceMode: "pentester",
  sidebarCollapsed: false,
  selectedVulnerabilityId: undefined,
  scanCreationOpen: false,
  toggleAudienceMode: () =>
    set((state) => ({
      audienceMode: state.audienceMode === "pentester" ? "executive" : "pentester"
    })),
  toggleSidebar: () =>
    set((state) => ({
      sidebarCollapsed: !state.sidebarCollapsed
    })),
  selectVulnerability: (id) => set({ selectedVulnerabilityId: id }),
  setScanCreationOpen: (open) => set({ scanCreationOpen: open })
}));
