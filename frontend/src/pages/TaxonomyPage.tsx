import React, { useEffect, useState } from "react";
import TaxonomyPanel from "../components/TaxonomyPanel";
import { DEFAULT_USER_ID, apiUrl } from "../api";

type Props = {
  datasetId?: string;
  onDatasetId?: (id: string) => void;
};

const TaxonomyPage: React.FC<Props> = ({ datasetId: initialId = "", onDatasetId }) => {
  const [datasetId, setDatasetId] = useState(initialId);
  const [yaml, setYaml] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialId) setDatasetId(initialId);
  }, [initialId]);

  const fetchYaml = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(apiUrl(`/api/users/${DEFAULT_USER_ID}/taxonomy`));
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Failed to fetch taxonomy");
      }
      const json = await res.json();
      setYaml(json.taxonomy_yaml || "");
      if (json.dataset_id) {
        setDatasetId(json.dataset_id);
        onDatasetId?.(json.dataset_id);
      }
    } catch (e: any) {
      setError(e?.message || "Failed to fetch taxonomy");
      setYaml("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-50">Taxonomy preview</h3>
      <p className="text-xs text-slate-400">
        Inspect the YAML router derived from your filterable columns. This is the structure the agent exposes to the
        model and uses for validation and backoff.
      </p>
      <div className="grid gap-3 sm:grid-cols-[minmax(0,1.6fr),auto] sm:items-end">
        <label className="text-xs text-slate-300">
          <span className="mb-1 block text-[11px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Current dataset ID
          </span>
          <input
            value={datasetId}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-100 placeholder:text-slate-500 focus:border-accent focus:outline-none"
            readOnly
            placeholder="Resolved from the current user’s dataset"
          />
        </label>
        <button
          type="button"
          onClick={fetchYaml}
          disabled={loading}
          className="inline-flex items-center justify-center rounded-full bg-accent px-3 py-1.5 text-xs font-semibold text-slate-950 shadow-sm shadow-sky-500/50 hover:bg-sky-300 transition-colors disabled:opacity-50"
        >
          {loading ? "Loading…" : "Load taxonomy"}
        </button>
      </div>
      {error && (
        <div className="rounded-xl border border-red-600/70 bg-red-950/40 px-3 py-2 text-xs text-red-100">
          {error}
        </div>
      )}
      {yaml && (
        <TaxonomyPanel
          yaml={yaml}
          onCopy={() => navigator.clipboard.writeText(yaml)}
        />
      )}
    </div>
  );
};

export default TaxonomyPage;
