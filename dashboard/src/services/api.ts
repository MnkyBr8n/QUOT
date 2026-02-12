export const API_BASE = 'http://localhost:8000';

export interface Stats {
  total_queries: number;
  total_sessions: number;
  total_errors: number;
  avg_response_time: number;
  total_tokens: number;
  total_docs_ingested: number;
  total_chunks_created: number;
  queries_today: number;
  error_rate: number;
}

export interface Session {
  session_id: string;
  start_time: string | null;
  end_time: string | null;
  query_count: number;
  total_response_time: number;
  avg_response_time: number;
  error_count: number;
  tokens_used: number;
  vendor: string | null;
  app: string | null;
}

export interface LogEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  session_id: string;
  vendor?: string;
  app?: string;
  query_id?: number;
  query?: string;
  answer?: string;
  response_time_s?: number;
  tokens_used?: number;
  num_sources?: number;
  sources?: Array<{ content: string; metadata: Record<string, unknown> }>;
  num_docs?: number;
  num_chunks?: number;
  ingestion_time_s?: number;
  error_type?: string;
  error_message?: string;
  extra?: Record<string, unknown>;
}

export interface ResponseTimeData {
  timestamp: string;
  response_time_s: number;
  query_id: number;
  session_id: string;
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function getStats(): Promise<Stats> {
  return fetchJson<Stats>('/logs/stats');
}

export async function getSessions(): Promise<Session[]> {
  return fetchJson<Session[]>('/logs/sessions');
}

export async function getSessionDetail(sessionId: string): Promise<{
  session_id: string;
  events: LogEvent[];
  query_count: number;
  error_count: number;
  total_response_time: number;
  avg_response_time: number;
  tokens_used: number;
  start_time: string | null;
  end_time: string | null;
  vendor: string | null;
  app: string | null;
}> {
  return fetchJson(`/logs/sessions/${sessionId}`);
}

export async function getEvents(params?: {
  event_type?: string;
  session_id?: string;
  limit?: number;
  offset?: number;
}): Promise<{ events: LogEvent[]; count: number }> {
  const searchParams = new URLSearchParams();
  if (params?.event_type) searchParams.set('event_type', params.event_type);
  if (params?.session_id) searchParams.set('session_id', params.session_id);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  if (params?.offset) searchParams.set('offset', params.offset.toString());

  const query = searchParams.toString();
  return fetchJson(`/logs/events${query ? `?${query}` : ''}`);
}

export async function getQueries(limit = 100, offset = 0): Promise<{ queries: LogEvent[]; count: number }> {
  return fetchJson(`/logs/queries?limit=${limit}&offset=${offset}`);
}

export async function getErrors(limit = 50): Promise<{ errors: LogEvent[]; count: number }> {
  return fetchJson(`/logs/errors?limit=${limit}`);
}

export async function getResponseTimes(limit = 100): Promise<{ data: ResponseTimeData[]; count: number }> {
  return fetchJson(`/logs/response-times?limit=${limit}`);
}
