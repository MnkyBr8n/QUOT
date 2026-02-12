import { useState } from 'react';
import { Dashboard, Sessions, Queries, Errors } from './pages';
import { API_BASE } from './services/api';

type Page = 'dashboard' | 'sessions' | 'queries' | 'errors';

const navItems: { id: Page; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'sessions', label: 'Sessions', icon: '📋' },
  { id: 'queries', label: 'Queries', icon: '💬' },
  { id: 'errors', label: 'Errors', icon: '⚠️' },
];

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'sessions':
        return <Sessions />;
      case 'queries':
        return <Queries />;
      case 'errors':
        return <Errors />;
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold">RAG Logger</h1>
          <p className="text-xs text-gray-400 mt-1">Unified Dashboard</p>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => setCurrentPage(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                    currentPage === item.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800'
                  }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-700 text-xs text-gray-500">
          <p>API: {API_BASE}</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-6 overflow-auto">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
