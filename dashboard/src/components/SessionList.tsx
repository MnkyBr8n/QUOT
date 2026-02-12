import type { Session } from '../services/api';

interface SessionListProps {
  sessions: Session[];
  onSelect?: (session: Session) => void;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  try {
    return new Date(dateStr).toLocaleString();
  } catch {
    return dateStr;
  }
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs.toFixed(0)}s`;
}

export function SessionList({ sessions, onSelect }: SessionListProps) {
  if (sessions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No sessions found
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Session ID
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Start Time
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Queries
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Avg Response
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Errors
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Tokens
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Vendor
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sessions.map((session) => (
            <tr
              key={session.session_id}
              onClick={() => onSelect?.(session)}
              className={onSelect ? 'cursor-pointer hover:bg-gray-50' : ''}
            >
              <td className="px-4 py-3 whitespace-nowrap">
                <span className="text-sm font-mono text-gray-900">
                  {session.session_id.slice(0, 20)}...
                </span>
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {formatDate(session.start_time)}
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {session.query_count}
                </span>
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {session.avg_response_time.toFixed(2)}s
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                {session.error_count > 0 ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    {session.error_count}
                  </span>
                ) : (
                  <span className="text-sm text-gray-400">0</span>
                )}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {session.tokens_used.toLocaleString()}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {session.vendor || '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
