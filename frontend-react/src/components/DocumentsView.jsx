import { useState, useRef } from 'react';
import { Upload, FileText, Trash2, CheckCircle, AlertCircle } from 'lucide-react';
import { publishDocument, getFiles, clearCollection, deleteFile } from '../api';

const DocumentsView = ({ fileList, onRefresh }) => {
    const fileInputRef = useRef(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState([]); // { name, progress, status, error }
    const [filterStatus, setFilterStatus] = useState('all'); // all, completed, pending, failed

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleUpload(e.dataTransfer.files[0]);
        }
    };

    const handleFileSelect = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleUpload(e.target.files[0]);
        }
    };

    const handleUpload = async (file) => {
        const newFile = {
            id: Date.now(),
            name: file.name,
            progress: 0,
            status: 'pending' // Renamed from uploading to match filter
        };

        setUploadingFiles(prev => [newFile, ...prev]);

        // Mock Progress
        const interval = setInterval(() => {
            setUploadingFiles(prev => prev.map(f =>
                f.id === newFile.id && f.progress < 90 ? { ...f, progress: f.progress + 10 } : f
            ));
        }, 300);

        try {
            const result = await publishDocument(file);
            clearInterval(interval);

            if (result.success) {
                // Success: Remove from uploadingFiles so it doesn't show as duplicate
                // It will appear in fileList after refresh
                setUploadingFiles(prev => prev.filter(f => f.id !== newFile.id));
                onRefresh(); // Refresh global file list
            } else {
                setUploadingFiles(prev => prev.map(f =>
                    f.id === newFile.id ? { ...f, progress: 100, status: 'failed', error: result.message } : f
                ));
            }
        } catch (error) {
            clearInterval(interval);
            setUploadingFiles(prev => prev.map(f =>
                f.id === newFile.id ? { ...f, progress: 100, status: 'failed', error: error.message } : f
            ));
        }
    };

    const handleDelete = async (filename) => {
        if (confirm(`Are you sure you want to delete "${filename}"?`)) {
            await deleteFile(filename);
            onRefresh();
        }
    };

    const handleClearAll = async () => {
        if (confirm("Are you sure you want to delete ALL documents?")) {
            await clearCollection();
            onRefresh();
            setUploadingFiles([]); // Also clear any failed/pending status
        }
    };

    // Unified List Logic
    const getFilteredList = () => {
        const pendingItems = uploadingFiles.filter(f => f.status === 'pending');
        const failedItems = uploadingFiles.filter(f => f.status === 'failed');
        const completedItems = fileList.map(name => ({ name, status: 'completed' }));

        let merged = [];
        if (filterStatus === 'all') {
            merged = [...pendingItems, ...failedItems, ...completedItems];
        } else if (filterStatus === 'pending') {
            merged = pendingItems;
        } else if (filterStatus === 'failed') {
            merged = failedItems;
        } else if (filterStatus === 'completed') {
            merged = completedItems;
        }
        return merged;
    };

    const displayList = getFilteredList();

    return (
        <div className="flex-1 p-8 overflow-y-auto bg-slate-50">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h2 className="text-2xl font-brand text-secondary mb-1">Document Management</h2>
                        <div className="flex items-center gap-2">
                            <select
                                value={filterStatus}
                                onChange={(e) => setFilterStatus(e.target.value)}
                                className="bg-white border border-slate-300 text-slate-600 text-sm rounded-lg focus:ring-primary focus:border-primary block px-3 py-1.5 shadow-sm outline-none"
                            >
                                <option value="all">View All</option>
                                <option value="completed">Completed</option>
                                <option value="pending">Pending</option>
                                <option value="failed">Failed</option>
                            </select>
                            <span className="text-xs font-medium text-slate-400">
                                {displayList.length} items
                            </span>
                        </div>
                    </div>

                    <button
                        onClick={handleClearAll}
                        className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
                    >
                        <Trash2 size={16} /> Delete All Docs
                    </button>
                </div>

                {/* Upload Area */}
                <div
                    className={`
                        mb-10 p-10 border-2 border-dashed rounded-xl text-center transition-all bg-white shadow-sm
                        ${dragActive ? 'border-primary bg-primary/5' : 'border-slate-300 hover:border-primary/50'}
                    `}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current.click()}
                >
                    <input
                        ref={fileInputRef}
                        type="file"
                        className="hidden"
                        accept=".pdf,.txt,.docx"
                        onChange={handleFileSelect}
                    />
                    <div className="w-16 h-16 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Upload size={32} />
                    </div>
                    <h3 className="text-lg font-semibold text-secondary mb-2">Click to upload or drag and drop</h3>
                    <p className="text-slate-500 text-sm">PDF, DOCX, or TXT (Max 10MB)</p>
                </div>

                {/* Unified File List Table */}
                <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-slate-50">
                            <tr>
                                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Document Name</th>
                                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Upload Date</th>
                                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {displayList.length === 0 ? (
                                <tr>
                                    <td colSpan="4" className="p-8 text-center text-slate-400">
                                        {filterStatus === 'all' ? "No documents found." : `No ${filterStatus} documents.`}
                                    </td>
                                </tr>
                            ) : (
                                displayList.map((file, idx) => (
                                    <tr key={idx} className="border-t border-slate-100 hover:bg-slate-50 transition-colors group">
                                        <td className="p-4 flex items-center gap-3 font-medium text-secondary">
                                            <div className={`w-8 h-8 rounded flex items-center justify-center
                                                ${file.status === 'failed' ? 'bg-red-50 text-red-500' :
                                                    file.status === 'pending' ? 'bg-yellow-50 text-yellow-500' : 'bg-blue-50 text-blue-600'}
                                            `}>
                                                {file.status === 'failed' ? <AlertCircle size={16} /> : <FileText size={16} />}
                                            </div>
                                            <div>
                                                <div className="truncate max-w-[200px]" title={file.name}>{file.name}</div>
                                                {file.error && <div className="text-[10px] text-red-500">{file.error}</div>}
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize
                                                ${file.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                    file.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                                        file.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-800'}
                                            `}>
                                                {file.status === 'pending' ? `Uploading ${file.progress}%` : file.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-sm text-slate-500">
                                            {new Date().toLocaleDateString()}
                                        </td>
                                        <td className="p-4 text-sm text-slate-500 text-right">
                                            {file.status === 'completed' && (
                                                <button
                                                    onClick={() => handleDelete(file.name)}
                                                    className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                                                    title="Delete File"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            )}
                                            {file.status === 'failed' && (
                                                <button
                                                    onClick={() => setUploadingFiles(prev => prev.filter(f => f.id !== file.id))}
                                                    className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                                                    title="Dismiss"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default DocumentsView;
