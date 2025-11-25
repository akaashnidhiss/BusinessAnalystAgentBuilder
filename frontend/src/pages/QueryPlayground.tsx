import React, { useEffect, useState } from "react";
import ResultsTable from "../components/ResultsTable";
import DiagPanel from "../components/DiagPanel";
import { apiUrl, getJson } from "../api";

type Props = {
  datasetId?: string;
  onDatasetId?: (id: string) => void;
};

const QueryPlayground: React.FC<Props> = ({ datasetId: initialId = "", onDatasetId }) => {
  const [datasetId, setDatasetId] = useState(initialId);
  const [dimensionOrder, setDimensionOrder] = useState<string[]>([]);
  const [dimensionValues, setDimensionValues] = useState<Record<string, string[]>>({});
  const [selectedFilters, setSelectedFilters] = useState<Record<string, string[]>>({});
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [diag, setDiag] = useState<any>(null);
  const [limit, setLimit] = useState<number | undefined>(50);
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [nlQuery, setNlQuery] = useState("");
  const [agentLog, setAgentLog] = useState<string[]>([]);
  const [loadingDimensions, setLoadingDimensions] = useState(false);
  const [dimensionsError, setDimensionsError] = useState<string | null>(null);

  useEffect(() => {
    if (initialId) setDatasetId(initialId);
  }, [initialId]);

  useEffect(() => {
    const loadDimensions = async () => {
      if (!datasetId) {
        setDimensionOrder([]);
        setDimensionValues({});
        return;
      }
      setLoadingDimensions(true);
      setDimensionsError(null);
      try {
        const data = await getJson<{
          dataset_id: string;
          dims: string[];
          values: Record<string, string[]>;
        }>(`/api/datasets/${datasetId}/dimensions`);
        setDimensionOrder(data.dims || []);
        setDimensionValues(data.values || {});
      } catch (e: any) {
        setDimensionsError(e?.message || "Failed to load dimensions. Ensure ETL has been run.");
        setDimensionOrder([]);
        setDimensionValues({});
      } finally {
        setLoadingDimensions(false);
      }
    };
    loadDimensions();
  }, [datasetId]);

  const appendLog = (line: string) => {
    setAgentLog((prev) => [...prev, line]);
  };

  const toggleFilterValue = (dim: string, value: string) => {
    setSelectedFilters((prev) => {
      const existing = prev[dim] || [];
      const exists = existing.includes(value);
      const nextValues = exists ? existing.filter((v) => v !== value) : [...existing, value];
      return { ...prev, [dim]: nextValues };
    });
  };

  const deriveFiltersFromNaturalLanguage = () => {
    const text = nlQuery.trim();
    if (!text) {
      appendLog("No natural language query provided. Skipping interpretation.");
      return;
    }
    const lower = text.toLowerCase();
    const nextFilters: Record<string, string[]> = {};
    appendLog(`Agent received natural language intent: "${text}"`);

    dimensionOrder.forEach((dim) => {
      const vals = dimensionValues[dim] || [];
      vals.forEach((val) => {
        const valLower = String(val).toLowerCase();
        if (valLower && lower.includes(valLower)) {
          if (!nextFilters[dim]) nextFilters[dim] = [];
          if (!nextFilters[dim].includes(val)) {
            nextFilters[dim].push(val);
            appendLog(`Matched value "${val}" for dimension "${dim}".`);
          }
        }
      });
    });

    if (!Object.keys(nextFilters).length) {
      appendLog("No dimension values matched directly from the text. You can still pick filters manually.");
    } else {
      appendLog(`Proposed filters: ${JSON.stringify(nextFilters)}`);
      setSelectedFilters((prev) => ({ ...prev, ...nextFilters }));
    }
  };

  const runQuery = async () => {
    setError(null);
    setStatus("");
    if (!datasetId) {
      setError("Please provide a dataset ID before querying.");
      return;
    }
    const payload = {
      dataset_id: datasetId,
      filters: selectedFilters,
      limit,
    };
    setRunning(true);
    setStatus("Running query…");
    appendLog(`Executing query with filters: ${JSON.stringify(payload.filters)} and limit=${payload.limit ?? "default"}.`);
    try {
      const res = await fetch(apiUrl("/api/query"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Query failed");
      }
      const json = await res.json();
      setRows(json.rows || []);
      setDiag(json.diag || null);
      onDatasetId?.(datasetId);
      setStatus(`Returned ${json.row_count ?? (json.rows?.length ?? 0)} rows`);
      appendLog(`Query succeeded with ${json.row_count ?? (json.rows?.length ?? 0)} rows.`);
    } catch (e: any) {
      setError(e?.message || "Query failed");
      setRows([]);
      setDiag(null);
      appendLog("Query failed. See error banner for details.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-50">Query playground</h3>
      <p className="text-xs text-slate-400">
        Use validated filters to query this agent. Behind the scenes, the backend checks your filters against the
        taxonomy, performs backoff if needed, and runs a safe DuckDB query.
      </p>

      <div className="grid gap-3 md:grid-cols-[minmax(0,1.8fr),auto] md:items-end">
        <label className="text-xs text-slate-300">
          <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Dataset ID
          </span>
          <input
            value={datasetId}
            onChange={(e) => setDatasetId(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
            placeholder="dataset_id that backs this agent"
          />
        </label>
        <label className="text-xs text-slate-300">
          <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Row limit
          </span>
          <input
            type="number"
            min={1}
            max={1000}
            value={limit ?? ""}
            onChange={(e) => setLimit(e.target.value ? Number(e.target.value) : undefined)}
            className="w-28 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
          />
        </label>
      </div>

      <label className="text-xs text-slate-300">
        <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
          Natural language intent
        </span>
        <textarea
          value={nlQuery}
          onChange={(e) => setNlQuery(e.target.value)}
          rows={2}
          placeholder='e.g. "Shortlist APAC suppliers under $10M spend with low delivery risk."'
          className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
        />
        <p className="mt-1 text-[11px] text-slate-500">
          This is where your per-agent LLM will live. For now, we heuristically match values mentioned in the text to
          known dimension values.
        </p>
      </label>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Filter dimensions
          </span>
          {loadingDimensions && <span className="text-[11px] text-slate-400">Loading dimensions…</span>}
        </div>
        {dimensionsError && (
          <div className="rounded-xl border border-red-600/70 bg-red-950/40 px-3 py-2 text-xs text-red-100">
            {dimensionsError}
          </div>
        )}
        {!dimensionsError && !loadingDimensions && !dimensionOrder.length && (
          <p className="text-[11px] text-slate-500">
            No dimensions available yet. Make sure ETL has been run for this dataset.
          </p>
        )}
        {dimensionOrder.length > 0 && (
          <div className="space-y-3 rounded-xl border border-slate-800 bg-slate-950/80 p-3">
            {dimensionOrder.map((dim) => {
              const values = dimensionValues[dim] || [];
              const selected = selectedFilters[dim] || [];
              return (
                <div key={dim} className="space-y-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-medium text-slate-200">{dim}</span>
                    <span className="text-slate-500">
                      {selected.length} selected · {values.length} values
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {values.map((val) => {
                      const isActive = selected.includes(val);
                      return (
                        <button
                          key={val}
                          type="button"
                          onClick={() => toggleFilterValue(dim, val)}
                          className={[
                            "rounded-full border px-2 py-0.5 text-[11px] transition-colors",
                            isActive
                              ? "border-accent bg-accent/20 text-accent"
                              : "border-slate-700 bg-slate-950 text-slate-300 hover:border-slate-500",
                          ].join(" ")}
                        >
                          {val}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between gap-2">
        <button
          type="button"
          onClick={deriveFiltersFromNaturalLanguage}
          className="inline-flex items-center gap-1 rounded-full border border-slate-700 bg-slate-950 px-3 py-1.5 text-[11px] font-medium text-slate-200 hover:border-accent hover:text-accent transition-colors"
        >
          Let agent suggest filters
        </button>
        <button
          type="button"
          onClick={runQuery}
          disabled={running}
          className="inline-flex items-center gap-1 rounded-full bg-accent px-3 py-1.5 text-xs font-semibold text-slate-950 shadow-sm shadow-sky-500/50 hover:bg-sky-300 transition-colors disabled:opacity-50"
        >
          {running ? "Running…" : "Run query"}
        </button>
      </div>

      {agentLog.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-950/80 px-3 py-2 text-[11px] text-slate-200">
          <div className="mb-1 flex items-center justify-between">
            <span className="font-semibold text-slate-100">Agent thinking log</span>
            <span className="rounded-full bg-slate-900 px-2 py-0.5 text-[10px] text-slate-400">
              {agentLog.length} message{agentLog.length === 1 ? "" : "s"}
            </span>
          </div>
          <div className="max-h-40 space-y-1 overflow-auto font-mono">
            {agentLog.map((line, idx) => (
              <div key={idx} className="whitespace-pre-wrap text-[11px] text-slate-200">
                {line}
              </div>
            ))}
          </div>
        </div>
      )}

      {status && (
        <div className="rounded-xl border border-emerald-600/70 bg-emerald-950/40 px-3 py-2 text-xs text-emerald-100">
          {status}
        </div>
      )}
      {error && (
        <div className="rounded-xl border border-red-600/70 bg-red-950/40 px-3 py-2 text-xs text-red-100">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-[minmax(0,1.7fr),minmax(0,1.1fr)]">
        <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-3 text-xs text-slate-200">
          <ResultsTable rows={rows} />
        </div>
        <DiagPanel
          backoffLevel={diag?.backoff_level}
          reason={diag?.reason}
          canonical={diag?.used}
          counts={diag?.counts}
        />
      </div>
    </div>
  );
};

export default QueryPlayground;
