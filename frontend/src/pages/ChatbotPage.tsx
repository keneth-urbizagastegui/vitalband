// frontend/src/pages/ChatbotPage.tsx
import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { queryChatbot } from "../api/endpoints";

type ChatMessage = {
  sender: "user" | "bot";
  text: string;
};

export default function ChatbotPage() {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll hacia el final cuando se agrega un mensaje nuevo
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, loading]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const userText = message.trim();
    if (!userText || loading) return;

    // Agrega mensaje del usuario al historial
    setHistory((prev) => [...prev, { sender: "user", text: userText }]);
    setMessage("");
    setLoading(true);

    try {
      const { reply } = await queryChatbot(userText);
      setHistory((prev) => [...prev, { sender: "bot", text: reply }]);
    } catch (err) {
      console.error("Error consultando al chatbot:", err);
      setHistory((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Lo siento, no pude procesar tu mensaje en este momento. Por favor, inténtalo de nuevo más tarde.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto h-full flex flex-col">
      {/* Encabezado */}
      <div className="px-6 py-4 border-b bg-white">
        <h1 className="text-xl font-semibold text-ink">Asistente IA</h1>
        <p className="text-sm text-muted">Haz tus preguntas sobre la app y métricas de salud (sin consejos médicos).</p>
      </div>

      {/* Área de Chat */}
      <div className="flex-1 overflow-y-auto px-4 py-6 bg-slate-50">
        <div className="flex flex-col gap-3">
          {history.map((msg, idx) => (
            <div
              key={idx}
              className={`max-w-[85%] rounded-2xl px-4 py-2 shadow-sm ${
                msg.sender === "user"
                  ? "self-end bg-primary-600 text-white"
                  : "self-start bg-slate-100 text-ink"
              }`}
            >
              {msg.text}
            </div>
          ))}

          {loading && (
            <div className="max-w-[70%] self-start rounded-2xl px-4 py-2 bg-slate-100 text-muted">
              Escribiendo...
            </div>
          )}

          {/* marcador de final para auto-scroll */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Formulario de entrada */}
      <form onSubmit={handleSubmit} className="border-t bg-white px-4 py-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Escribe tu mensaje..."
            className="flex-1 rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-600"
            disabled={loading}
          />
          <button
            type="submit"
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Enviando..." : "Enviar"}
          </button>
        </div>
      </form>
    </div>
  );
}