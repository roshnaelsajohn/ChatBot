import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import MessageBubble from './MessageBubble';

const ChatArea = ({ messages, onSendMessage, isProcessing }) => {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isProcessing]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !isProcessing) {
            onSendMessage(input);
            setInput('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className="flex-1 flex flex-col h-full relative">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-3 md:p-6 pb-32 md:pb-32">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 opacity-60 px-4">
                        <div className="w-16 h-16 md:w-20 md:h-20 border-2 border-border border-dashed rounded-full flex items-center justify-center mb-4">
                            <span className="text-3xl md:text-4xl">🤖</span>
                        </div>
                        <h2 className="text-lg md:text-xl font-semibold mb-2 text-center">Welcome to RAG Chatbot</h2>
                        <p className="max-w-md text-center text-sm">
                            Upload a document to get started, or switch to "General Knowledge" mode to chat with the AI directly.
                        </p>
                    </div>
                ) : (
                    <>
                        {messages.map((msg, i) => (
                            <MessageBubble
                                key={i}
                                role={msg.role}
                                content={msg.content}
                                sources={msg.sources}
                                sourceType={msg.source_type}
                            />
                        ))}
                        {isProcessing && (
                            <div className="flex justify-start mb-6 w-full">
                                <div className="flex items-center gap-2 px-4 py-3 bg-card border border-border rounded-lg rounded-tl-none">
                                    <div className="flex gap-1">
                                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce"></div>
                                    </div>
                                    <span className="text-xs text-gray-500 ml-2">Thinking...</span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </>
                )}
            </div>

            {/* Input Area */}
            <div className="absolute bottom-0 left-0 right-0 p-3 md:p-6 bg-gradient-to-t from-white via-white/80 to-transparent pt-8 md:pt-10
                            pb-[calc(0.75rem+env(safe-area-inset-bottom,0px))] md:pb-6">
                <form
                    onSubmit={handleSubmit}
                    className="relative flex items-end gap-2 bg-white border border-border rounded-2xl p-2 md:p-3 shadow-xl hover:shadow-2xl hover:border-primary/30 transition-all focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/10"
                >
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask a question..."
                        className="flex-1 bg-transparent border-none text-text placeholder-gray-600 resize-none max-h-32 min-h-[40px] md:min-h-[44px] py-2 md:py-3 px-2 focus:ring-0 text-sm"
                        disabled={isProcessing}
                        rows={1}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isProcessing}
                        className={`
                            p-2 rounded-lg mb-1 transition-all shrink-0
                            ${!input.trim() || isProcessing
                                ? 'text-gray-600 cursor-not-allowed'
                                : 'bg-primary text-white hover:bg-primary/90 shadow-md'}
                        `}
                    >
                        <Send size={18} />
                    </button>
                </form>
                <div className="text-center mt-2 text-[10px] text-gray-600">
                    AI can make mistakes. Check important info.
                </div>
            </div>
        </div>
    );
};

export default ChatArea;
