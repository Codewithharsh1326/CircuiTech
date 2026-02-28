import { useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { Send, Cpu, Loader2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDesignStore } from "@/stores/designStore";
import api from "@/lib/api";

export default function ChatPanel() {
  const chatHistory = useDesignStore((s) => s.chatHistory);
  const addMessage = useDesignStore((s) => s.addMessage);
  const isLoading = useDesignStore((s) => s.isLoading);
  const setIsLoading = useDesignStore((s) => s.setIsLoading);
  const setBom = useDesignStore((s) => s.setBom);

  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  function scrollToBottom() {
    // Small delay so the DOM updates before we scroll
    setTimeout(() => {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 50);
  }

  async function handleSend() {
    const text = input.trim();
    if (!text) return;

    addMessage({ role: "user", content: text });
    setInput("");
    setIsLoading(true);
    scrollToBottom();

    try {
      const response = await api.post("/api/chat/", {
        message: text,
        history: chatHistory
      });
      const data = response.data;

      addMessage({
        role: "assistant",
        content: data.reply,
      });

      if (data.bom && data.bom.items) {
        setBom(data.bom.items);
      }

    } catch {
      addMessage({
        role: "assistant",
        content: "Sorry, I had trouble reaching the sourcing backend. Please ensure the server is running."
      });
    } finally {
      setIsLoading(false);
      scrollToBottom();
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    handleSend();
  }

  return (
    <div className="flex h-full flex-col bg-slate-950">
      {/* ── Header ──────────────────────────────────────────── */}
      <header className="flex shrink-0 items-center justify-between border-b border-slate-800 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-emerald-500/10">
            <Cpu className="size-5 text-emerald-400" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-semibold text-slate-100">
              Co-Pilot
            </span>
            <span className="text-xs text-slate-500">Groq · Llama-3 70B</span>
          </div>
        </div>
        <Badge
          variant="outline"
          className="ml-auto border-emerald-500/30 text-emerald-400"
        >
          Online
        </Badge>
      </header>

      {/* ── Messages ────────────────────────────────────────── */}
      <ScrollArea className="flex-1 px-4 py-4">
        {chatHistory.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-2 pt-24 text-center">
            <Cpu className="size-10 text-slate-700" />
            <p className="text-sm text-slate-500">
              Describe your embedded system design and I'll source the
              components.
            </p>
          </div>
        )}

        <div className="flex flex-col gap-3">
          {chatHistory.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"
                }`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed ${msg.role === "user"
                  ? "rounded-br-sm bg-emerald-600 text-white"
                  : "rounded-bl-sm border border-slate-800 bg-slate-900 text-slate-300"
                  }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {/* ── Progress Indicator ────────────────────────────────── */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex max-w-[85%] items-center gap-2 rounded-xl rounded-bl-sm border border-slate-800 bg-slate-900/50 px-4 py-3 text-sm text-slate-400">
                <Loader2 className="size-4 animate-spin text-emerald-500" />
                Searching part databases...
              </div>
            </div>
          )}

          {/* Invisible scroll anchor */}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* ── Input bar ───────────────────────────────────────── */}
      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-2 border-t border-slate-800 px-4 py-3"
      >
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your design requirements…"
          className="flex-1 border-slate-700 bg-slate-900 text-slate-200 placeholder:text-slate-600 focus-visible:border-emerald-500/50 focus-visible:ring-emerald-500/20"
        />
        <Button
          type="submit"
          size="icon"
          disabled={!input.trim()}
          className="shrink-0 bg-emerald-600 text-white hover:bg-emerald-500 disabled:opacity-40"
        >
          <Send className="size-4" />
        </Button>
      </form>
    </div>
  );
}
