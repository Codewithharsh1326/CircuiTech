import { create } from "zustand";
import api, { SESSION_ID } from "../lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface BomItem {
  partNumber: string;
  manufacturer?: string;
  description: string;
  quantity: number;
  estimatedCost: number;
}

interface Connection {
  source_part: string;
  source_pin: string;
  target_part: string;
  target_pin: string;
  signal_type: string;
  description: string;
}

interface DesignState {
  sessionId: string;
  chatHistory: ChatMessage[];
  currentBom: BomItem[];
  pinConnections: Connection[];
  activeTab: string;
  isLoading: boolean;

  addMessage: (message: ChatMessage) => void;
  setBom: (bom: BomItem[]) => void;
  setActiveTab: (tab: string) => void;
  setIsLoading: (loading: boolean) => void;
  generatePinMap: () => Promise<void>;
  resetSession: () => void;
}

export const useDesignStore = create<DesignState>((set, get) => ({
  sessionId: SESSION_ID,
  chatHistory: [],
  currentBom: [],
  pinConnections: [],
  activeTab: "bom",
  isLoading: false,

  addMessage: (message) =>
    set((state) => ({ chatHistory: [...state.chatHistory, message] })),

  setBom: (bom) => set({ currentBom: bom }),

  setActiveTab: (tab) => set({ activeTab: tab }),

  setIsLoading: (loading: boolean) => set({ isLoading: loading }),

  generatePinMap: async () => {
    const { currentBom } = get();
    if (currentBom.length === 0) return;

    set({ isLoading: true, activeTab: "pinmap" });
    try {
      const response = await api.post("/api/pinmap/", { items: currentBom });
      set({ pinConnections: response.data.connections || [] });
    } catch (error) {
      console.error("Failed to generate pin map", error);
    } finally {
      set({ isLoading: false });
    }
  },

  resetSession: () =>
    set({ chatHistory: [], currentBom: [], pinConnections: [], activeTab: "bom", isLoading: false }),
}));
