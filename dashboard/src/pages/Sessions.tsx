import { useEffect, useState } from 'react';
import { SessionList } from '../components';
import { getSessions, getSessionDetail, type Session, type LogEvent } from '../services/api';

export function Sessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<{
    session_id: string;
    events: LogEvent[];
    query_count: number;
    error_count: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSessions() {
      try {
        setLoading(true);
        const data = await getSessions();
        setSessions(data);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to fetch sessions');
      } finally {
        setLoading(false);
      }
    }

    fetchSessions();
  }, []);

  const handleSelectSession = async (session: Session) => {
    try {
      const detail = await getSessionDetail(session.session_id);
      setSelectedSession(detail);
    } catch (e) {
      console.error('Failed to fetch session detail:', e);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading sessions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Sessions</h1>

      <div className="bg-white rounded-lg shadow">
        <SessionList sessions={sessions} onSelect={handleSelectSession} />
      </div>

      {/* Session Detail Modal */}
      {selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b flex justify-between items-center">
              <h2 className="text-lg font-semibold">
                Session: {selectedSession.session_id.slice(0, 30)}...
              </h2>
              <button
                onClick={() => setSelectedSession(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div className="p-4 space-y-4 overflow-y-auto max-h-[calc(80vh-60px)]">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded p-3">
                  <p className="text-xs text-blue-600 font-medium">Queries</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {selectedSession.query_count}
                  </p>
                </div>
                <div className="bg-red-50 rounded p-3">
                  <p className="text-xs text-red-600 font-medium">Errors</p>
                  <p className="text-2xl font-bold text-red-900">
                    {selectedSession.error_count}
                  </p>
                </div>
                <div className="bg-green-50 rounded p-3">
                  <p className="text-xs text-green-600 font-medium">Events</p>
                  <p className="text-2xl font-bold text-green-900">
                    {selectedSession.events.length}
                  </p>
                </div>
              </div>

              <h3 className="font-medium text-gray-700 mt-4">Events Timeline</h3>
              <div className="space-y-2">
                {selectedSession.events.map((event) => (
                  <div
                    key={event.event_id}
                    className={`p-3 rounded text-sm ${
                      event.event_type === 'error'
                        ? 'bg-red-50 border-l-4 border-red-400'
                        : event.event_type === 'query'
                        ? 'bg-blue-50 border-l-4 border-blue-400'
                        : 'bg-gray-50 border-l-4 border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between">
                      <span className="font-medium">{event.event_type}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    {event.query && (
                      <p className="text-gray-600 mt-1 truncate">
                        Q: {event.query}
                      </p>
                    )}
                    {event.error_message && (
                      <p className="text-red-600 mt-1">{event.error_message}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
