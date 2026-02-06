import { useState } from 'react';
import ChatArea from './ChatArea';
import { FileText, Globe, Brain, RotateCcw } from 'lucide-react';

const ChatView = ({
    messages,
    onSendMessage,
    isProcessing,
    chatMode,
    setChatMode,
    synthesizeResponse,
    setSynthesizeResponse,
    onClearChat
}) => {
    return (
        <div className="flex-1 flex h-full overflow-hidden">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col relative bg-white">
                <ChatArea
                    messages={messages}
                    onSendMessage={onSendMessage}
                    isProcessing={isProcessing}
                />
            </div>

            {/* Chat Controls (Right Panel) */}
            <div className="w-72 bg-slate-50 border-l border-border p-6 flex flex-col">
                <div className="mb-6 flex justify-between items-center">
                    <h3 className="text-sm font-bold text-secondary uppercase tracking-wider">Controls</h3>
                    <button
                        onClick={onClearChat}
                        className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                        title="Clear Chat"
                    >
                        <RotateCcw size={16} />
                    </button>
                </div>

                {/* Mode Selector */}
                <div className="mb-8">
                    <label className="text-xs font-semibold text-slate-500 mb-3 block">Source Mode</label>
                    <div className="space-y-2">
                        <button
                            onClick={() => setChatMode('document')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm border transition-all text-left ${chatMode === 'document' ? 'bg-white border-primary text-primary shadow-sm ring-1 ring-primary/20' : 'bg-white border-border text-slate-500 hover:border-slate-300'}`}
                        >
                            <FileText size={18} />
                            <span className="font-medium">Ask Documents</span>
                        </button>

                        <button
                            onClick={() => setChatMode('web')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm border transition-all text-left ${chatMode === 'web' ? 'bg-white border-primary text-primary shadow-sm ring-1 ring-primary/20' : 'bg-white border-border text-slate-500 hover:border-slate-300'}`}
                        >
                            <Globe size={18} />
                            <span className="font-medium">Web Search</span>
                        </button>

                        <button
                            onClick={() => setChatMode('llm')}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm border transition-all text-left ${chatMode === 'llm' ? 'bg-white border-primary text-primary shadow-sm ring-1 ring-primary/20' : 'bg-white border-border text-slate-500 hover:border-slate-300'}`}
                        >
                            <Brain size={18} />
                            <span className="font-medium">General Knowledge</span>
                        </button>
                    </div>
                </div>

                {/* Synthesize Toggle */}
                {chatMode !== 'llm' && (
                    <div className="p-4 bg-white border border-border rounded-xl shadow-sm">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-semibold text-secondary">Synthesize</span>
                            <button
                                onClick={() => setSynthesizeResponse(!synthesizeResponse)}
                                className={`w-11 h-6 rounded-full relative transition-colors ${synthesizeResponse ? 'bg-primary' : 'bg-slate-300'}`}
                            >
                                <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all shadow-sm ${synthesizeResponse ? 'left-6' : 'left-1'}`}></div>
                            </button>
                        </div>
                        <p className="text-xs text-slate-500 leading-relaxed">
                            {synthesizeResponse
                                ? "AI generates a complete answer using retrieved chunks."
                                : "Returns raw text chunks directly from the database."}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatView;
