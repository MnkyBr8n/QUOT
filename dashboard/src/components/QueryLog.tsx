import type { LogEvent } from '../services/api';

interface QueryLogProps {
  queries: LogEvent[];
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleString();
  } catch {
    return dateStr;
  }
}

function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.slice(0, length) + '...';
}

export function QueryLog({ queries }: QueryLogProps) {
  if (queries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No queries found
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {queries.map((query) => (
        <div
          key={query.event_id}
          className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-mono text-gray-400">
                  #{query.query_id}
                </span>
                <span className="text-xs text-gray-400">
                  {formatDate(query.timestamp)}
                </span>
                {query.response_time_s && (
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    query.response_time_s > 5 ? 'bg-red-100 text-red-700' :
                    query.response_time_s > 2 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-green-100 text-green-700'
                  }`}>
                    {query.response_time_s.toFixed(2)}s
                  </span>
                )}
                {query.tokens_used && (
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                    {query.tokens_used} tokens
                  </span>
                )}
              </div>

              <p className="text-sm font-medium text-gray-900 mb-1">
                Q: {query.query}
              </p>

              <p className="text-sm text-gray-600">
                A: {truncate(query.answer || '', 200)}
              </p>

              {query.num_sources !== undefined && query.num_sources > 0 && (
                <p className="text-xs text-gray-400 mt-2">
                  {query.num_sources} source{query.num_sources > 1 ? 's' : ''} retrieved
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
