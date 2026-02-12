import type { LogEvent } from '../services/api';

interface ErrorListProps {
  errors: LogEvent[];
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleString();
  } catch {
    return dateStr;
  }
}

export function ErrorList({ errors }: ErrorListProps) {
  if (errors.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No errors found - great!
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {errors.map((error) => (
        <div
          key={error.event_id}
          className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded font-medium">
                  {error.error_type}
                </span>
                <span className="text-xs text-gray-400">
                  {formatDate(error.timestamp)}
                </span>
              </div>

              <p className="text-sm font-medium text-gray-900 mb-1">
                {error.error_message}
              </p>

              {error.query && (
                <p className="text-xs text-gray-500 mt-2">
                  Query: "{error.query}"
                </p>
              )}

              <p className="text-xs text-gray-400 mt-1 font-mono">
                Session: {error.session_id?.slice(0, 20)}...
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
