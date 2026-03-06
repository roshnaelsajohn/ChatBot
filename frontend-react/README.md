# TestFly AI — React Frontend

The React/Vite frontend for the **TestFly AI RAG Chatbot**. Fully mobile-responsive, built with Tailwind CSS and Lucide icons.

---

## 🖼 UI Overview

| Screen | Desktop (≥768px) | Mobile (<768px) |
|---|---|---|
| Navigation | Left sidebar | Fixed bottom tab bar |
| Chat controls | Right panel (`w-72`) | FAB → bottom-sheet drawer |
| Documents list | 4-column table | Card list |

---

## 🚀 Getting Started

```bash
# Install dependencies
npm install

# Start dev server
npm run dev        # → http://localhost:5173

# Production build
npm run build
```

---

## 📁 Structure

```
src/
├── App.jsx               # Router + layout shell
├── api.js                # Axios API client (points to backend)
├── index.css             # Tailwind directives + Google Fonts
└── components/
    ├── Header.jsx         # Top header — compact on mobile
    ├── Navigation.jsx     # Sidebar (desktop) / Bottom tab bar (mobile)
    ├── ChatView.jsx       # Chat area + Controls panel / FAB drawer
    ├── ChatArea.jsx       # Message thread + input bar
    ├── MessageBubble.jsx  # Message bubble with source badges
    └── DocumentsView.jsx  # Upload + file management
```

---

## ⚙️ Environment

Create a `.env` file in this directory:

```env
VITE_API_BASE_URL=http://localhost:5001
```

---

## 📦 Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| react | ^19 | UI framework |
| react-router-dom | ^7 | Client-side routing |
| tailwindcss | ^4 | Utility-first styling |
| lucide-react | latest | Icons |
| axios | latest | HTTP client |
| react-markdown | latest | Markdown rendering in messages |
