"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Translations, getTranslations } from "@/utils/translations";
import { RecoilRoot } from "recoil";
import {
  ChainlitAPI,
  ChainlitContext,
  useChatMessages,
  useChatInteract,
} from "@chainlit/react-client";
import ErrorBoundary from "@/components/ErrorBoundary";

const apiClient = new ChainlitAPI();

function ChatComponent() {
  const [input, setInput] = useState<string>("");
  const [translations, setTranslations] = useState<Translations>(
    {} as Translations,
  );
  const searchParams = useSearchParams();
  const lang = searchParams?.get("lang") || "en";

  useEffect(() => {
    setTranslations(getTranslations(lang));
  }, [lang]);

  const { messages } = useChatMessages();
  const { sendMessage } = useChatInteract();

  const handleSendMessage = () => {
    if (input.trim()) {
      sendMessage({ content: input.trim(), id: Date.now().toString() });
      setInput("");
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <h1 className="text-2xl font-bold p-4">{translations.chatTitle}</h1>
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message) => (
          <div key={message.id} className="mb-4">
            <strong>{message.role}:</strong> {message.content}
          </div>
        ))}
      </div>
      <div className="p-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={translations.typeMessage}
          className="w-full p-2 border rounded"
        />
        <button
          onClick={handleSendMessage}
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
        >
          {translations.send}
        </button>
      </div>
    </div>
  );
}

export default function Chat() {
  return (
    <ErrorBoundary>
      <ChainlitContext.Provider value={apiClient}>
        <RecoilRoot>
          <ChatComponent />
        </RecoilRoot>
      </ChainlitContext.Provider>
    </ErrorBoundary>
  );
}
