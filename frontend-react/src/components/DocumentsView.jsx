import { useState, useRef } from 'react';
import { Upload, FileText, Trash2, CheckCircle, AlertCircle } from 'lucide-react';
import { publishDocument, getFiles, clearCollection } from '../api';

const DocumentsView = ({ fileList, onRefresh }) => {
    const fileInputRef = useRef(null);
    const [dragActive, setDragActive] = useState(false);
    const [uploadingFiles, setUploadingFiles] = useState([]); // { name, progress, status, error }

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
            status: 'uploading'
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
                setUploadingFiles(prev => prev.map(f =>
                    f.id === newFile.id ? { ...f, progress: 100, status: 'completed' } : f
                ));
                onRefresh(); // Refresh global file list
            } else {
                setUploadingFiles(prev => prev.map(f =>
                    f.id === newFile.id ? { ...f, progress: 100, status: 'error', error: result.message } : f
                ));
            }
        } catch (error) {
            clearInterval(interval);
            setUploadingFiles(prev => prev.map(f =>
                f.id === newFile.id ? { ...f, progress: 100, status: 'error', error: error.message } : f
            ));
        }
    };

    const handleClearAll = async () => {
        if (confirm("Are you sure you want to delete ALL documents?")) {
            await clearCollection();
            onRefresh();
            setUploadingFiles([]);
        }
    };

    return (
        <div className="flex-1 p-8 overflow-y-auto bg-slate-50">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h2 className="text-2xl font-brand text-secondary">Document Management</h2>
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

                {/* Upload Progress */}
                {uploadingFiles.length > 0 && (
                    <div className="mb-8 space-y-3">
                        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">Recent Uploads</h3>
                        {uploadingFiles.map((file) => (
                            <div key={file.id} className="bg-white p-4 rounded-lg border border-border shadow-sm flex items-center gap-4">
                                <FileText className="text-slate-400" size={24} />
                                <div className="flex-1">
                                    <div className="flex justify-between mb-1">
                                        <span className="text-sm font-medium text-secondary">{file.name}</span>
                                        <span className={`text-xs font-semibold ${file.status === 'error' ? 'text-red-500' : 'text-green-600'}`}>
                                            {file.status === 'error' ? 'Failed' : file.status === 'completed' ? 'Completed' : `${file.progress}%`}
                                        </span>
                                    </div>
                                    <div className="w-full bg-slate-100 rounded-full h-2">
                                        <div
                                            className={`h-2 rounded-full transition-all duration-300 ${file.status === 'error' ? 'bg-red-500' : 'bg-green-500'}`}
                                            style={{ width: `${file.progress}%` }}
                                        ></div>
                                    </div>
                                    {file.error && <p className="text-xs text-red-500 mt-1">{file.error}</p>}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* File List Table */}
                <div className="bg-white rounded-xl border border-border shadow-sm overflow-hidden">
                    <table className="w-full text-left border-collapse">
                        <thead className="bg-slate-50">
                            <tr>
                                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Document Name</th>
                                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Upload Date</th>
                                <th className="p-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Size</th>
                            </tr>
                        </thead>
                        <tbody>
                            {fileList.length === 0 ? (
                                <tr>
                                    <td colSpan="3" className="p-8 text-center text-slate-400">No documents found.</td>
                                </tr>
                            ) : (
                                fileList.map((file, idx) => (
                                    <tr key={idx} className="border-t border-slate-100 hover:bg-slate-50 transition-colors">
                                        <td className="p-4 flex items-center gap-3 font-medium text-secondary">
                                            <div className="w-8 h-8 rounded bg-blue-50 text-blue-600 flex items-center justify-center">
                                                <FileText size={16} />
                                            </div>
                                            {file}
                                        </td>
                                        <td className="p-4 text-sm text-slate-500">
                                            {new Date().toLocaleDateString()} {/* Mock Date since backend doesn't provide it yet */}
                                        </td>
                                        <td className="p-4 text-sm text-slate-500 text-right">
                                            -- KB {/* Mock Size */}
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
