import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { DEFAULT_USER_ID, getJson } from "../api";

type DatasetSummary = {
  dataset_id: string;
  display_name: string;
  dims: string[];
  metrics: string[];
  stats: Record<string, unknown>;
  taxonomy_yaml: string;
  is_current: boolean;
};

const AgentUniversePage: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [universeQuery, setUniverseQuery] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getJson<DatasetSummary[]>(`/api/users/${DEFAULT_USER_ID}/datasets`);
        setDatasets(data);
      } catch (err: any) {
        setError(err?.message || "Failed to load agents");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-slate-800 bg-gradient-to-br from-surface to-surfaceAlt p-6 shadow-lg shadow-slate-950/40">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Universe</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-50">
              What do you want your data agent to do?
            </h2>
            <p className="mt-2 max-w-xl text-sm text-slate-400">
              Upload a table, choose your filter dimensions and metrics, and Agent Studio will turn it into a
              queryable, taxonomy-backed agent.
            </p>
          </div>
          <div className="hidden text-right text-xs text-slate-400 md:block">
            <p className="font-medium text-slate-300">Two common patterns</p>
            <p>Supplier shortlisting · BOM finder</p>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-4 md:flex-row md:items-end">
          <div className="flex-1">
            <label className="text-xs font-medium uppercase tracking-[0.16em] text-slate-400">
              Central command
            </label>
            <div className="mt-2 flex items-center gap-3 rounded-2xl border border-slate-700/80 bg-slate-950/70 px-4 py-3 shadow-inner shadow-slate-950/60 focus-within:border-accent/80">
              <span className="rounded-full bg-slate-900 px-2 py-0.5 text-[11px] text-slate-400">/ask</span>
              <input
                value={universeQuery}
                onChange={(e) => setUniverseQuery(e.target.value)}
                placeholder="“Shortlist suppliers in APAC under $10M spend with low delivery risk.”"
                className="flex-1 bg-transparent text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none"
              />
            </div>
            <p className="mt-2 text-[11px] text-slate-500">
              For now this is a planning surface — pick an agent below to actually run queries.
            </p>
          </div>
          <div className="flex gap-2 md:flex-col md:items-end">
            <Link
              to="/agents/new"
              className="inline-flex items-center justify-center gap-1 rounded-xl bg-accent px-4 py-2 text-sm font-medium text-slate-950 shadow-sm shadow-sky-500/50 hover:bg-sky-300 transition-colors"
            >
              <span className="text-base leading-none">＋</span>
              New agent from data
            </Link>
            <Link
              to="/upload"
              className="inline-flex items-center justify-center rounded-xl border border-slate-700 bg-slate-900/60 px-4 py-2 text-xs font-medium text-slate-200 hover:border-slate-500 transition-colors"
            >
              Legacy dataset flow
            </Link>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-3 text-[11px] text-slate-400">
          <span className="rounded-full border border-slate-700 bg-slate-950/80 px-3 py-1">
            Try: “Find BOMs using [material] in [region].”
          </span>
          <span className="rounded-full border border-slate-700 bg-slate-950/80 px-3 py-1">
            Try: “List top 10 suppliers by spend in [category].”
          </span>
        </div>
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-100">Your agents</h3>
          <p className="text-xs text-slate-500">
            {loading
              ? "Loading agents…"
              : datasets.length
              ? `${datasets.length} dataset-backed agent${datasets.length === 1 ? "" : "s"}`
              : "No agents yet — upload your first dataset."}
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/60 bg-red-950/40 px-4 py-3 text-xs text-red-200">
            {error}
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2">
          {datasets.map((ds) => (
            <article
              key={ds.dataset_id}
              className="flex flex-col justify-between rounded-2xl border border-slate-800 bg-slate-950/60 p-4 shadow-sm shadow-slate-950/60"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-sm font-semibold text-slate-50">
                    Agent for{" "}
                    <span className="font-mono text-[12px] text-slate-300">
                      {ds.display_name || ds.dataset_id}
                    </span>
                  </h4>
                  <span className="rounded-full bg-slate-900 px-2 py-0.5 text-[10px] font-medium uppercase tracking-[0.18em] text-slate-400">
                    {ds.taxonomy_yaml?.trim()
                      ? "Ready"
                      : (ds.dims || []).length
                      ? "Configured"
                      : "Uploaded"}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  {ds.taxonomy_yaml?.trim()
                    ? "Taxonomy and validation are in place. You can query this agent."
                    : (ds.dims || []).length
                    ? "Config set — taxonomy was generated during dataset creation."
                    : "CSV uploaded — choose filter dimensions and metrics next."}
                </p>
              </div>

              <div className="mt-4 flex items-center justify-between gap-2 text-[11px]">
                <div className="flex flex-wrap gap-1.5">
                  <span className="rounded-full bg-slate-900 px-2 py-0.5 text-slate-400">
                    id: <code className="font-mono">{ds.dataset_id.slice(0, 8)}…</code>
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 ${
                      (ds.dims || []).length ? "bg-emerald-900/70 text-emerald-200" : "bg-slate-900 text-slate-500"
                    }`}
                  >
                    config
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 ${
                      ds.taxonomy_yaml?.trim() ? "bg-sky-900/70 text-sky-200" : "bg-slate-900 text-slate-500"
                    }`}
                  >
                    taxonomy
                  </span>
                  {ds.is_current && (
                    <span className="rounded-full bg-slate-900 px-2 py-0.5 text-slate-300">
                      current
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  <Link
                    to={`/agents/${ds.dataset_id}`}
                    className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-medium text-slate-950 hover:bg-slate-200 transition-colors"
                  >
                    Open agent
                  </Link>
                  {!ds.has_config && (
                    <Link
                      to="/agents/new"
                      className="hidden rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-[11px] font-medium text-slate-300 hover:border-slate-500 transition-colors sm:inline-flex"
                    >
                      Configure
                    </Link>
                  )}
                </div>
              </div>
            </article>
          ))}

          {!loading && !datasets.length && !error && (
            <div className="rounded-2xl border border-dashed border-slate-700/80 bg-slate-950/40 p-6 text-sm text-slate-400">
              <p className="font-medium text-slate-200">You don’t have any agents yet.</p>
              <p className="mt-1">
                Start by uploading a CSV — we’ll inspect its columns, help you choose filterable dimensions and
                retrievable metrics, and generate a taxonomy-backed agent.
              </p>
              <Link
                to="/agents/new"
                className="mt-4 inline-flex items-center gap-1 rounded-full bg-accent/90 px-3 py-1.5 text-xs font-medium text-slate-950 hover:bg-sky-300 transition-colors"
              >
                <span className="text-base leading-none">＋</span> Create your first agent
              </Link>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default AgentUniversePage;
