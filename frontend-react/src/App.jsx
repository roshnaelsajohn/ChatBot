import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Navigation from './components/Navigation';
import ChatView from './components/ChatView';
import DocumentsView from './components/DocumentsView';
import { getStats, getFiles, sendChat, clearCollection } from './api';

function App() {
  // Global State
  const [messages, setMessages] = useState([]);
  const [fileList, setFileList] = useState([]);
  const [stats, setStats] = useState({ total_chunks: 0 });
  const [isProcessing, setIsProcessing] = useState(false);

  // Chat Settings
  const [chatMode, setChatMode] = useState('document');
  const [synthesizeResponse, setSynthesizeResponse] = useState(true);

  useEffect(() => {
    refreshData();
  }, []);

  const refreshData = async () => {
    const s = await getStats();
    const f = await getFiles();
    setStats(s);
    setFileList(f);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  const handleSendMessage = async (text) => {
    // Add user message
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsProcessing(true);

    const response = await sendChat(text, chatMode, synthesizeResponse);

    setIsProcessing(false);

    if (response.success) {
      const botMsg = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        source_type: response.source_type
      };
      setMessages(prev => [...prev, botMsg]);
    } else {
      const errorMsg = {
        role: 'assistant',
        content: `⚠️ Error: ${response.message || 'Unknown error'}`
      };
      setMessages(prev => [...prev, errorMsg]);
    }
  };

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-background text-text overflow-hidden font-sans flex-col">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <Navigation />
          <main className="flex-1 flex flex-col relative overflow-hidden bg-slate-50">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route
                path="/dashboard"
                element={
                  <ChatView
                    messages={messages}
                    onSendMessage={handleSendMessage}
                    isProcessing={isProcessing}
                    chatMode={chatMode}
                    setChatMode={setChatMode}
                    synthesizeResponse={synthesizeResponse}
                    setSynthesizeResponse={setSynthesizeResponse}
                    onClearChat={handleClearChat}
                  />
                }
              />
              <Route
                path="/documents"
                element={
                  <DocumentsView
                    fileList={fileList}
                    onRefresh={refreshData}
                  />
                }
              />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App;
