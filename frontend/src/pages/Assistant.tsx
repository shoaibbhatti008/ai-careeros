import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Bot,
  Brain,
  Loader2,
  MessageSquarePlus,
  Send,
  Sparkles,
  Trash2,
  User,
} from "lucide-react";
import { clsx } from "clsx";

import { extractErrorMessage } from "@/lib/api";
import {
  createConversation,
  deleteConversation,
  getConversation,
  listConversations,
  sendMessage,
  type Conversation,
  type Message,
} from "@/lib/assistant";

export default function Assistant() {
  const queryClient = useQueryClient();
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // List conversations
  const {
    data: conversations = [],
    isLoading: isLoadingList,
  } = useQuery({
    queryKey: ["conversations"],
    queryFn: () => listConversations(),
  });

  // Active conversation detail
  const {
    data: activeConversation,
    isLoading: isLoadingActive,
  } = useQuery({
    queryKey: ["conversation", activeConversationId],
    queryFn: () => getConversation(activeConversationId as string),
    enabled: !!activeConversationId,
  });

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (activeConversation?.messages?.length) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [activeConversation?.messages]);

  // Auto-select first conversation
  useEffect(() => {
    if (!activeConversationId && conversations.length > 0) {
      setActiveConversationId(conversations[0].id);
    }
  }, [conversations, activeConversationId]);

  // Create new conversation
  const createMutation = useMutation({
    mutationFn: () =>
      createConversation({ title: "New conversation" }),
    onSuccess: (conv) => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      setActiveConversationId(conv.id);
    },
  });

  // Delete conversation
  const deleteMutation = useMutation({
    mutationFn: deleteConversation,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      if (activeConversationId === id) {
        setActiveConversationId(null);
      }
    },
  });

  // Send message
  const sendMutation = useMutation({
    mutationFn: (content: string) =>
      sendMessage(activeConversationId as string, { content }),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["conversation", activeConversationId],
      });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      setInput("");
    },
  });

  function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || !activeConversationId || sendMutation.isPending) return;
    sendMutation.mutate(input.trim());
  }

  function handleNewConversation() {
    createMutation.mutate();
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between animate-slide-up">
        <div>
          <p className="text-xs sm:text-sm font-semibold uppercase tracking-widest text-gold-600">
            AI
          </p>
          <h1 className="mt-2 text-2xl sm:text-3xl md:text-4xl font-bold text-cream-900 text-shadow-soft">
            Career Assistant
          </h1>
          <p className="mt-1 text-sm sm:text-base text-cream-600">
            Chat with specialized AI agents about your career.
          </p>
        </div>
        <button
          type="button"
          onClick={handleNewConversation}
          disabled={createMutation.isPending}
          className="btn-primary self-start sm:self-auto"
        >
          {createMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <MessageSquarePlus className="h-4 w-4" />
          )}
          New chat
        </button>
      </div>

      {/* Main layout — chat */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[280px_1fr] lg:gap-6 animate-slide-up" style={{ animationDelay: "0.1s" }}>
        {/* Sidebar — conversations list (hidden on small screens unless we add a toggle) */}
        <aside className="glass-card p-4 sm:p-5 lg:max-h-[calc(100vh-14rem)] lg:overflow-y-auto">
          <h2 className="mb-3 text-xs font-bold uppercase tracking-widest text-gold-700">
            Conversations
          </h2>

          {isLoadingList ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-gold-500" />
            </div>
          ) : conversations.length === 0 ? (
            <p className="py-4 text-center text-xs text-cream-500">
              No conversations yet
            </p>
          ) : (
            <ul className="space-y-1.5">
              {conversations.map((conv) => (
                <ConversationItem
                  key={conv.id}
                  conversation={conv}
                  isActive={conv.id === activeConversationId}
                  onClick={() => setActiveConversationId(conv.id)}
                  onDelete={() => {
                    if (confirm(`Delete "${conv.title}"?`)) {
                      deleteMutation.mutate(conv.id);
                    }
                  }}
                />
              ))}
            </ul>
          )}
        </aside>

        {/* Main chat area */}
        <div className="glass-card flex flex-col min-h-[500px] lg:min-h-[calc(100vh-14rem)] lg:max-h-[calc(100vh-14rem)]">
          {!activeConversationId ? (
            <EmptyChatState onNew={handleNewConversation} />
          ) : isLoadingActive ? (
            <div className="flex flex-1 items-center justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-gold-500" />
            </div>
          ) : (
            <>
              {/* Header */}
              <div className="flex items-center gap-3 border-b border-gold-400/20 p-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold text-cream-900">
                    {activeConversation?.title || "Untitled"}
                  </p>
                  <p className="text-[10px] uppercase tracking-widest text-cream-500">
                    Multi-Agent AI
                  </p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
                {(!activeConversation?.messages ||
                  activeConversation.messages.length === 0) && (
                  <p className="py-12 text-center text-sm text-cream-500">
                    Send a message to begin.
                  </p>
                )}
                {activeConversation?.messages?.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}

                {sendMutation.isPending && <TypingBubble />}

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <form
                onSubmit={handleSend}
                className="border-t border-gold-400/20 p-4"
              >
                <div className="flex items-end gap-2">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend(e);
                      }
                    }}
                    placeholder="Ask about your resume, jobs, skills, or interviews..."
                    rows={1}
                    disabled={sendMutation.isPending}
                    className="input resize-none flex-1 min-h-[44px] max-h-40"
                  />
                  <button
                    type="submit"
                    disabled={
                      sendMutation.isPending || !input.trim()
                    }
                    className="btn-primary flex-shrink-0"
                    aria-label="Send message"
                  >
                    {sendMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </button>
                </div>
                {sendMutation.isError && (
                  <p className="mt-2 text-xs text-red-600 animate-slide-down">
                    {extractErrorMessage(sendMutation.error)}
                  </p>
                )}
                <p className="mt-2 text-[10px] text-cream-500">
                  Press Enter to send · Shift + Enter for new line
                </p>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Sub-components
// ============================================================

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

function ConversationItem({
  conversation,
  isActive,
  onClick,
  onDelete,
}: ConversationItemProps) {
  return (
    <li>
      <div
        className={clsx(
          "group flex items-center gap-2 rounded-lg px-3 py-2 text-sm cursor-pointer transition-all duration-200",
          isActive
            ? "bg-gradient-to-r from-gold-400/30 to-gold-500/20 text-gold-900 border border-gold-400/40 shadow-gold"
            : "text-cream-700 hover:bg-gold-400/10 hover:text-gold-800"
        )}
        onClick={onClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") onClick();
        }}
      >
        <Brain className="h-3.5 w-3.5 flex-shrink-0" />
        <span className="flex-1 truncate">{conversation.title || "Untitled"}</span>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="flex h-6 w-6 items-center justify-center rounded opacity-0 group-hover:opacity-100 hover:bg-red-500/10 hover:text-red-600 transition-all"
          aria-label="Delete conversation"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    </li>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={clsx(
        "flex items-start gap-3 animate-slide-up",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl shadow-lg transition-transform duration-300 hover:scale-110",
          isUser
            ? "bg-gradient-to-br from-blue-500 to-cyan-500 shadow-blue-500/40"
            : "bg-gradient-to-br from-gold-400 to-gold-600 shadow-gold-400/40"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-white" />
        ) : (
          <Sparkles className="h-4 w-4 text-white" />
        )}
      </div>

      {/* Bubble */}
      <div
        className={clsx(
          "max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap break-words",
          isUser
            ? "bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-400/30 text-cream-900"
            : "glass border border-gold-400/20 text-cream-800"
        )}
      >
        {message.content}
      </div>
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="flex items-start gap-3 animate-slide-up">
      <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-lg shadow-gold-400/40">
        <Sparkles className="h-4 w-4 text-white" />
      </div>
      <div className="glass rounded-2xl px-4 py-3 border border-gold-400/20">
        <div className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-gold-500 animate-bounce" style={{ animationDelay: "0s" }} />
          <span className="h-2 w-2 rounded-full bg-gold-500 animate-bounce" style={{ animationDelay: "0.15s" }} />
          <span className="h-2 w-2 rounded-full bg-gold-500 animate-bounce" style={{ animationDelay: "0.3s" }} />
        </div>
      </div>
    </div>
  );
}

function EmptyChatState({ onNew }: { onNew: () => void }) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-2xl shadow-gold-400/40 animate-float-slow">
        <Brain className="h-10 w-10 text-white" />
      </div>
      <h3 className="mt-6 text-xl font-bold text-cream-900">
        Start a conversation
      </h3>
      <p className="mt-2 max-w-md text-sm text-cream-600">
        Ask about resumes, jobs, skills, interviews, or anything career-related.
        Our specialized agents will help.
      </p>
      <button type="button" onClick={onNew} className="btn-primary mt-6">
        <MessageSquarePlus className="h-4 w-4" />
        New conversation
      </button>
    </div>
  );
}