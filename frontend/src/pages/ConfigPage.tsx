import React, { useEffect, useState } from "react";
import { DEFAULT_USER_ID, apiUrl } from "../api";

type Props = {
  datasetId?: string;
  onDatasetId?: (id: string) => void;
  uploadId?: string | null;
};

const ConfigPage: React.FC<Props> = ({ datasetId: initialId = "", onDatasetId, uploadId }) => {
  const [datasetId, setDatasetId] = useState(initialId);
  const [filterable, setFilterable] = useState("");
  const [retrievable, setRetrievable] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialId) setDatasetId(initialId);
  }, [initialId]);

  const saveConfig = async () => {
    setError(null);
    setStatus("");
    if (!uploadId) {
      setError("Please upload a CSV and generate a preview before saving configuration.");
      return;
    }
    const payload = {
      upload_id: uploadId,
      dims: filterable.split(",").map((s) => s.trim()).filter(Boolean),
      metrics: retrievable.split(",").map((s) => s.trim()).filter(Boolean),
      display_name: datasetId || undefined,
    };
    try {
      const res = await fetch(apiUrl(`/api/users/${DEFAULT_USER_ID}/datasets`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Failed to create dataset");
      }
      const json = await res.json();
      const createdId = json.dataset_id as string;
      setDatasetId(createdId);
      onDatasetId?.(createdId);
      setStatus(
        `Dataset created. id=${createdId}, dims=${(json.dims || []).join(
          ", "
        )}, metrics=${(json.metrics || []).join(", ")}`
      );
    } catch (e: any) {
      setError(e?.message || "Failed to create dataset");
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-50">Schema configuration</h3>
      <p className="text-xs text-slate-400">
        Tell the agent which columns are categorical filters and which are retrievable metrics or attributes. You can
        refine this later as you explore the taxonomy.
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="text-xs text-slate-300">
          <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Dataset name (optional)
          </span>
          <input
            value={datasetId}
            onChange={(e) => setDatasetId(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
            placeholder="e.g. APAC suppliers (will auto-generate an id)"
          />
        </label>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="text-xs text-slate-300">
          <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Filterable columns
          </span>
          <input
            value={filterable}
            onChange={(e) => setFilterable(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
            placeholder="e.g. l1, region, l2, l3"
          />
          <p className="mt-1 text-[11px] text-slate-500">
            Categorical dimensions that drive routing, like L1, region, category, risk band.
          </p>
        </label>
        <label className="text-xs text-slate-300">
          <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Retrievable columns
          </span>
          <input
            value={retrievable}
            onChange={(e) => setRetrievable(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
            placeholder="e.g. supplier_name, spend, risk_score"
          />
          <p className="mt-1 text-[11px] text-slate-500">
            Columns that can appear in query results — scores, links, descriptions, etc.
          </p>
        </label>
      </div>
      <button
        type="button"
        onClick={saveConfig}
        className="inline-flex items-center gap-1 rounded-full bg-accent px-3 py-1.5 text-xs font-semibold text-slate-950 shadow-sm shadow-sky-500/50 hover:bg-sky-300 transition-colors"
      >
        Save configuration
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

export default ConfigPage;
