import { useEffect, useState } from 'react';
import { ErrorList } from '../components';
import { getErrors, type LogEvent } from '../services/api';

export function Errors() {
  const [errors, setErrors] = useState<LogEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchErrors() {
      try {
        setLoading(true);
        const data = await getErrors(50);
        setErrors(data.errors);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to fetch errors');
      } finally {
        setLoading(false);
      }
    }

    fetchErrors();
  }, []);

  if (loading && errors.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading errors...</div>
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
        <h1 className="text-2xl font-bold text-gray-900">Error Log</h1>
        <span className="text-sm text-gray-500">
          {errors.length} error{errors.length !== 1 ? 's' : ''} found
        </span>
      </div>

      {errors.length === 0 ? (
        <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
          <span className="text-4xl mb-4 block">✅</span>
          <p className="text-green-700 font-medium">No errors logged</p>
          <p className="text-green-600 text-sm mt-1">
            Your system is running smoothly!
          </p>
        </div>
      ) : (
        <ErrorList errors={errors} />
      )}
    </div>
  );
}
