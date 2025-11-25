import React, { useEffect, useState } from "react";
import { apiUrl } from "../api";

type Props = {
  datasetId?: string;
  onDatasetId?: (id: string) => void;
};

const EtlPage: React.FC<Props> = ({ datasetId: initialId = "", onDatasetId }) => {
  const [datasetId, setDatasetId] = useState(initialId);
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (initialId) setDatasetId(initialId);
  }, [initialId]);

  const runEtl = async () => {
    setError(null);
    setStatus("");
    if (!datasetId) {
      setError("Please provide a dataset ID before running ETL.");
      return;
    }
    setRunning(true);
    setStatus("Running ETL…");
    try {
      const res = await fetch(apiUrl(`/api/datasets/${datasetId}/etl`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: datasetId }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "ETL failed");
      }
      const json = await res.json();
      setStatus(`ETL done. rows=${json.stats?.rows}, leaf_rows=${json.stats?.leaf_rows}`);

      // initialize DuckDB right after ETL
      const initRes = await fetch(apiUrl(`/api/datasets/${datasetId}/duckdb/init`), { method: "POST" });
      if (!initRes.ok) {
        const text = await initRes.text();
        throw new Error(text || "DuckDB init failed");
      }
      onDatasetId?.(datasetId);
    } catch (e: any) {
      setError(e?.message || "ETL or DuckDB init failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-50">ETL + DuckDB initialization</h3>
      <p className="text-xs text-slate-400">
        Normalize the dataset, build a leaf index for all valid filter combinations, render the taxonomy YAML, and load
        the normalized data into an in-memory DuckDB table.
      </p>
      <label className="block text-xs text-slate-300">
        <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
          Dataset ID
        </span>
        <input
          value={datasetId}
          onChange={(e) => setDatasetId(e.target.value)}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
          placeholder="Use the dataset_id from the upload step"
        />
      </label>
      <button
        type="button"
        onClick={runEtl}
        disabled={running}
        className="inline-flex items-center gap-1 rounded-full bg-accent px-3 py-1.5 text-xs font-semibold text-slate-950 shadow-sm shadow-sky-500/50 hover:bg-sky-300 transition-colors disabled:opacity-50"
      >
        {running ? "Running ETL…" : "Run ETL + Init DuckDB"}
      </button>
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
    </div>
  );
};

export default EtlPage;
