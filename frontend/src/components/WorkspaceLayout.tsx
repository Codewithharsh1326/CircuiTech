import { Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import ChatPanel from "@/components/ChatPanel";
import DashboardPanel from "@/components/DashboardPanel";

export default function WorkspaceLayout() {
  return (
    <div className="relative h-screen w-full overflow-hidden bg-slate-950">
      {/* ── Main Canvas ────────────────────────────────────────────── */}
      <DashboardPanel />

      {/* ── Floating AI Co-Pilot ───────────────────────────────────── */}
      <Sheet>
        <SheetTrigger asChild>
          <Button
            size="icon"
            className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-emerald-600 shadow-xl shadow-emerald-900/40 transition-transform hover:scale-105 hover:bg-emerald-500 focus-visible:ring-emerald-500"
          >
            <Bot className="size-6 text-white" />
          </Button>
        </SheetTrigger>
        <SheetContent
          side="right"
          className="w-full max-w-sm border-l border-slate-800 bg-slate-950 p-0 sm:max-w-md"
        >
          <ChatPanel />
        </SheetContent>
      </Sheet>
    </div>
  );
}
