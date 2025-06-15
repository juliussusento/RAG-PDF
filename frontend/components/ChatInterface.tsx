import React, { useState } from 'react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: any[];
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userMessage.content,
          chat_history: updatedMessages.map((msg) => ({
            role: msg.type,
            content: msg.content
          }))
        })
      });

      const data = await res.json();
      const assistantMessage: Message = {
        id: Date.now().toString() + '-a',
        type: 'assistant',
        content: data.answer,
        sources: data.sources,
      };

      setMessages([...updatedMessages, assistantMessage]);
    } catch (err) {
      setMessages([...updatedMessages, {
        id: 'error',
        type: 'assistant',
        content: '❌ Terjadi kesalahan saat mengambil jawaban.',
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-8 p-4 border rounded-xl shadow-sm bg-white">
      <h2 className="text-xl font-semibold mb-4 text-center">💬 Chat with Document</h2>
      
      <div className="h-96 overflow-y-auto space-y-4 mb-4 p-2 bg-gray-50 rounded-md border">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-3 rounded-lg shadow-sm w-fit max-w-full ${
              msg.type === 'user' ? 'bg-blue-100 ml-auto text-right' : 'bg-gray-100'
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>

            {msg.type === 'assistant' && msg.sources?.length > 0 && (
              <div className="mt-2 text-sm text-gray-600">
                <strong>Sumber:</strong>
                <ul className="list-disc ml-5 mt-1 space-y-1">
                  {msg.sources.map((src, idx) => (
                    <li key={idx}>
                      <span className="italic text-gray-700">Page {src.page}:</span>{" "}
                      <span>{src.content.slice(0, 100)}...</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {isLoading && <p className="text-center text-gray-500 italic">⏳ Loading...</p>}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyPress}
          placeholder="Tanyakan sesuatu..."
          className="flex-1 p-2 border rounded-md"
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Kirim
        </button>
      </div>
    </div>
  );
}
