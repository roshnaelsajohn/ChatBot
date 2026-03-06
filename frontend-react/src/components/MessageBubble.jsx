import { User, Bot, FileText, Globe, Brain } from 'lucide-react';

const MessageBubble = ({ role, content, sources, sourceType }) => {
    const isUser = role === 'user';

    const getSourceIcon = () => {
        if (!sourceType) return null;
        if (sourceType.includes('Document')) return <FileText size={12} />;
        if (sourceType.includes('Web')) return <Globe size={12} />;
        return <Brain size={12} />;
    }

    return (
        <div className={`flex w-full mb-4 md:mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div className={`
                flex flex-col max-w-[95%] md:max-w-[80%]
                ${isUser ? 'items-end' : 'items-start'}
            `}>
                <div className={`
                    flex items-center gap-2 mb-1 px-1
                    ${isUser ? 'flex-row-reverse' : 'flex-row'}
                `}>
                    <div className={`
                        w-6 h-6 rounded flex items-center justify-center
                        ${isUser ? 'bg-primary text-white shadow-sm' : 'bg-slate-200 text-slate-600'}
                    `}>
                        {isUser ? <User size={14} /> : <Bot size={14} />}
                    </div>
                    <span className="text-xs text-slate-400 font-medium">
                        {isUser ? 'You' : 'AI Assistant'}
                    </span>
                </div>

                <div className={`
                    p-3 md:p-4 rounded-lg border text-sm leading-relaxed shadow-sm
                    ${isUser
                        ? 'bg-secondary border-secondary text-white rounded-tr-none'
                        : 'bg-white border-border text-slate-800 rounded-tl-none'}
                `}>
                    {/* Render Content */}
                    <div className="markdown-content">
                        {content.split('\n').map((line, i) => (
                            <p key={i} className="mb-2 last:mb-0 min-h-[1.2em]">{line}</p>
                        ))}
                    </div>

                    {/* Sources */}
                    {!isUser && sources && sources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-border/50">
                            <div className="flex flex-wrap gap-2">
                                {sources.map((src, idx) => (
                                    <span
                                        key={idx}
                                        className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-blue-50 border border-blue-100 rounded-md text-xs font-medium text-blue-700 hover:bg-blue-100 transition-colors cursor-default"
                                        title="Source Document"
                                    >
                                        <FileText size={12} className="text-blue-500" />
                                        {src}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Source Type */}
                    {!isUser && sourceType && (
                        <div className="flex items-center gap-1 mt-2 text-[10px] text-gray-600">
                            {getSourceIcon()}
                            <span>{sourceType}</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
