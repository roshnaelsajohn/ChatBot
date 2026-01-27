import axios from 'axios';

// Default to localhost:5000 if env var not set
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getStats = async () => {
    try {
        const response = await api.get('/stats');
        return response.data;
    } catch (error) {
        console.error("Error fetching stats:", error);
        return { total_chunks: 0 };
    }
};

export const getFiles = async () => {
    try {
        const response = await api.get('/files');
        return response.data.files || [];
    } catch (error) {
        console.error("Error fetching files:", error);
        return [];
    }
};

export const publishDocument = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await api.post('/publish', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            timeout: 300000, // 5 minutes for large files
        });
        return response.data;
    } catch (error) {
        console.error("Error publishing document:", error);
        if (error.response && error.response.status === 409) {
            return { success: false, message: "File already exists in the database." };
        }
        return { success: false, message: error.message };
    }
};

export const clearCollection = async () => {
    try {
        const response = await api.post('/clear');
        return response.data;
    } catch (error) {
        return { success: false, message: error.message };
    }
};

export const sendChat = async (message, chatMode, synthesizeResponse) => {
    try {
        const response = await api.post('/chat', {
            message,
            n_results: 10,
            chat_mode: chatMode,
            synthesize_response: synthesizeResponse,
        }, { timeout: 300000 });
        return response.data;
    } catch (error) {
        console.error("Error sending chat:", error);
        return { success: false, message: error.message };
    }
};

export default api;
