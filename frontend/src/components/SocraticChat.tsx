"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, Send, Sparkles, User, Bot, Lightbulb } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function SocraticChat({ topicTitle }: { topicTitle: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [lastDirective] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const userMsg = input.trim();
    if (!userMsg || isStreaming) return;

    setInput("");
    const newMessages: ChatMessage[] = [
      ...messages,
      { role: "user", content: userMsg },
      { role: "assistant", content: "" },
    ];
    setMessages(newMessages);
    setIsStreaming(true);

    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const response = await fetch(`${API_BASE_URL}/socratic/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          topic_title: topicTitle,
          user_message: userMsg,
          history: messages,
          skill_level: "beginner",
        }),
      });

      if (!response.body) throw new Error("No stream body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let accumulated = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;

        setMessages((prev) => {
          const updated = [...prev];
          if (updated.length > 0 && updated[updated.length - 1].role === "assistant") {
            updated[updated.length - 1] = {
              role: "assistant",
              content: accumulated,
            };
          }
          return updated;
        });
      }
    } catch (err) {
      console.error("Streaming error:", err);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <Card className="p-0 overflow-hidden border-2 border-black">
      {/* Header */}
      <div className="bg-black text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-display font-bold text-sm text-white">Socratic AI Tutor</h3>
            <p className="text-xs text-zinc-400">Multi-Agent Guided Q&A</p>
          </div>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-zinc-800 text-zinc-300 border border-zinc-700">
          Interactive
        </span>
      </div>

      {/* Curriculum Agent Directive banner */}
      {lastDirective && (
        <div className="bg-primary-50 border-b border-primary-200 p-3 flex items-start gap-2 text-xs text-primary-900">
          <Lightbulb className="w-4 h-4 text-primary-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Curriculum Agent Guidance: </span>
            {lastDirective}
          </div>
        </div>
      )}

      {/* Conversation Thread */}
      <div className="p-4 space-y-4 max-h-[350px] overflow-y-auto bg-zinc-50">
        {messages.length === 0 ? (
          <div className="py-8 text-center space-y-2">
            <MessageSquare className="w-8 h-8 text-zinc-400 mx-auto" />
            <p className="text-sm font-semibold text-black">Have questions about this topic?</p>
            <p className="text-xs text-zinc-500 max-w-xs mx-auto">
              Ask our Socratic AI Tutor. Rather than giving solutions, it asks guided questions to help you master the concept!
            </p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-7 h-7 rounded-lg bg-black text-white flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] p-3.5 rounded-2xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-primary-600 text-white font-medium rounded-tr-none"
                      : "bg-white border border-zinc-200 text-black font-normal shadow-card rounded-tl-none"
                  }`}
                >
                  {msg.content}
                </div>

                {msg.role === "user" && (
                  <div className="w-7 h-7 rounded-lg bg-primary-100 text-primary-700 flex items-center justify-center shrink-0 mt-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        )}

        {isStreaming && messages[messages.length - 1]?.content === "" && (
          <div className="flex gap-3 justify-start">
            <div className="w-7 h-7 rounded-lg bg-black text-white flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white border border-zinc-200 p-3 rounded-2xl text-xs text-zinc-500 animate-pulse">
              Socratic Agent is thinking…
            </div>
          </div>
        )}
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} className="p-3 bg-white border-t border-zinc-200 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question or explain your reasoning..."
          className="flex-1 px-4 py-2.5 text-sm rounded-xl border border-zinc-200 bg-zinc-50 text-black placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-black"
        />
        <Button
          type="submit"
          size="sm"
          disabled={!input.trim() || isStreaming}
          isLoading={isStreaming}
          rightIcon={<Send className="w-3.5 h-3.5" />}
        >
          Ask
        </Button>
      </form>
    </Card>
  );
}
