import { useEffect, useState } from 'react';
import { StatCard } from '../components';
import { getStats, getResponseTimes, type Stats, type ResponseTimeData } from '../services/api';

export function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [responseTimes, setResponseTimes] = useState<ResponseTimeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [statsData, rtData] = await Promise.all([
          getStats(),
          getResponseTimes(50),
        ]);
        setStats(statsData);
        setResponseTimes(rtData.data);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
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

  if (!stats) return null;

  const maxResponseTime = responseTimes.length > 0
    ? Math.max(...responseTimes.map(r => r.response_time_s))
    : 1;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Queries"
          value={stats.total_queries.toLocaleString()}
          subtitle={`${stats.queries_today} today`}
          icon="💬"
        />
        <StatCard
          title="Avg Response Time"
          value={`${stats.avg_response_time.toFixed(2)}s`}
          icon="⚡"
        />
        <StatCard
          title="Total Sessions"
          value={stats.total_sessions.toLocaleString()}
          icon="📊"
        />
        <StatCard
          title="Error Rate"
          value={`${stats.error_rate.toFixed(1)}%`}
          subtitle={`${stats.total_errors} errors`}
          icon={stats.error_rate > 5 ? '⚠️' : '✅'}
        />
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          title="Total Tokens"
          value={stats.total_tokens.toLocaleString()}
          icon="🔤"
        />
        <StatCard
          title="Docs Ingested"
          value={stats.total_docs_ingested.toLocaleString()}
          subtitle={`${stats.total_chunks_created} chunks`}
          icon="📄"
        />
        <StatCard
          title="Chunks Created"
          value={stats.total_chunks_created.toLocaleString()}
          icon="🧩"
        />
      </div>

      {/* Response Time Chart (simple bar representation) */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Response Times
        </h2>
        {responseTimes.length > 0 ? (
          <div className="flex items-end gap-1 h-32">
            {responseTimes.slice(0, 50).reverse().map((rt, i) => {
              const height = (rt.response_time_s / maxResponseTime) * 100;
              const color = rt.response_time_s > 5 ? 'bg-red-400' :
                           rt.response_time_s > 2 ? 'bg-yellow-400' : 'bg-green-400';
              return (
                <div
                  key={i}
                  className={`flex-1 ${color} rounded-t`}
                  style={{ height: `${Math.max(height, 5)}%` }}
                  title={`${rt.response_time_s.toFixed(2)}s`}
                />
              );
            })}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No response time data yet</p>
        )}
        <div className="flex justify-between text-xs text-gray-400 mt-2">
          <span>Oldest</span>
          <span>Most Recent</span>
        </div>
      </div>
    </div>
  );
}
