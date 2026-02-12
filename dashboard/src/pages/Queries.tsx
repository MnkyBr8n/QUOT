import { useEffect, useState } from 'react';
import { QueryLog } from '../components';
import { getQueries, type LogEvent } from '../services/api';

export function Queries() {
  const [queries, setQueries] = useState<LogEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    async function fetchQueries() {
      try {
        setLoading(true);
        const data = await getQueries(pageSize, page * pageSize);
        setQueries(data.queries);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to fetch queries');
      } finally {
        setLoading(false);
      }
    }

    fetchQueries();
  }, [page]);

  if (loading && queries.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading queries...</div>
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
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Query Log</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1 text-sm bg-white border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          <span className="px-3 py-1 text-sm text-gray-500">
            Page {page + 1}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={queries.length < pageSize}
            className="px-3 py-1 text-sm bg-white border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next →
          </button>
        </div>
      </div>

      <QueryLog queries={queries} />
    </div>
  );
}
