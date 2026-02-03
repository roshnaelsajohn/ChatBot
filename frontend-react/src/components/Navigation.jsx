import { useState } from 'react';
import { MessageCircle, FileText } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const Navigation = ({ fileList = [], onRefresh }) => {
    const [showAllFiles, setShowAllFiles] = useState(false);

    const navItems = [
        { path: '/dashboard', label: 'Ask AI', icon: MessageCircle },
        { path: '/documents', label: 'Documents', icon: FileText },
    ];

    return (
        <nav className="w-64 h-full bg-secondary border-r border-slate-700 flex flex-col py-6">
            <div className="px-4 mb-6">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Menu</span>
            </div>
            <div className="flex flex-col gap-1 px-3 mb-8">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `
                            flex items-center gap-3 px-3 py-3 rounded-lg text-sm font-medium transition-all justify-between
                            ${isActive
                                ? 'bg-primary text-white shadow-md'
                                : 'text-slate-400 hover:bg-slate-800 hover:text-white'}
                        `}
                    >
                        <div className="flex items-center gap-3">
                            <item.icon size={20} />
                            {item.label}
                        </div>
                        {item.path === '/documents' && fileList.length > 0 && (
                            <span className="bg-slate-700 text-white text-[10px] px-2 py-0.5 rounded-full">
                                {fileList.length}
                            </span>
                        )}
                    </NavLink>
                ))}
            </div>

            {/* File List Section */}
            <div className="px-4 mb-2 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Loaded Documents</span>
                <button
                    onClick={onRefresh}
                    className="text-slate-500 hover:text-primary transition-colors"
                    title="Refresh List"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" /><path d="M3 3v5h5" /><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" /><path d="M16 21h5v-5" /></svg>
                </button>
            </div>
            <div className="flex-1 overflow-y-auto px-3">
                {fileList && fileList.length > 0 ? (
                    <div className="space-y-1">
                        {fileList.slice(0, showAllFiles ? fileList.length : 5).map((file, idx) => (
                            <div key={idx} className="flex items-center gap-2 px-3 py-2 text-xs text-slate-400 truncate hover:text-slate-200">
                                <FileText size={14} className="shrink-0" />
                                <span className="truncate" title={file}>{file}</span>
                            </div>
                        ))}

                        {fileList.length > 5 && (
                            <button
                                onClick={() => setShowAllFiles(!showAllFiles)}
                                className="w-full text-left px-3 py-2 text-xs text-primary hover:text-primary/80 font-medium flex items-center gap-1"
                            >
                                {showAllFiles ? "Show Less" : `Show ${fileList.length - 5} More`}
                            </button>
                        )}
                    </div>
                ) : (
                    <div className="px-3 py-2 text-xs text-slate-600 italic">
                        No documents uploaded
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navigation;
