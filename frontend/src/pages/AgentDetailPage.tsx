import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import QueryPlayground from "./QueryPlayground";
import TaxonomyPanel from "../components/TaxonomyPanel";
import { DEFAULT_USER_ID, getJson } from "../api";

type Props = {
  onDatasetId?: (id: string) => void;
};

type TaxonomyResponse = {
  dataset_id: string;
  taxonomy_yaml: string;
  stats?: Record<string, number>;
  dims?: string[];
};

const AgentDetailPage: React.FC<Props> = ({ onDatasetId }) => {
  const params = useParams();
  const [datasetId, setDatasetId] = useState<string>(params.datasetId || "");
  const [taxonomy, setTaxonomy] = useState<TaxonomyResponse | null>(null);
  const [loadingTaxonomy, setLoadingTaxonomy] = useState(false);
  const [taxonomyError, setTaxonomyError] = useState<string | null>(null);

  useEffect(() => {
    if (params.datasetId) {
      setDatasetId(params.datasetId);
      onDatasetId?.(params.datasetId);
    }
  }, [params.datasetId, onDatasetId]);

  useEffect(() => {
    const loadTaxonomy = async () => {
      setLoadingTaxonomy(true);
      setTaxonomyError(null);
      try {
        const data = await getJson<TaxonomyResponse>(`/api/users/${DEFAULT_USER_ID}/taxonomy`);
        if (data.dataset_id) {
          setDatasetId(data.dataset_id);
          onDatasetId?.(data.dataset_id);
        }
        setTaxonomy(data);
      } catch (err: any) {
        setTaxonomyError(err?.message || "Failed to load taxonomy. Ensure ETL has been run.");
        setTaxonomy(null);
      } finally {
        setLoadingTaxonomy(false);
      }
    };
    loadTaxonomy();
  }, [datasetId]);

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-3 border-b border-slate-800 pb-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Agent</p>
          <h2 className="mt-1 text-lg font-semibold text-slate-50">Dataset-backed agent</h2>
          <p className="mt-1 text-xs text-slate-400">
            Query this agent using validated filters, and inspect the taxonomy that constrains its routing.
          </p>
        </div>
        {datasetId && (
          <div className="rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-[11px] text-slate-300">
            <div className="text-slate-400">dataset_id</div>
            <code className="mt-0.5 block max-w-xs truncate font-mono text-[11px] text-slate-50">
              {datasetId}
            </code>
          </div>
        )}
      </header>

      {!datasetId && (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/60 p-6 text-sm text-slate-400">
          No dataset_id was provided in the URL. Go back to the Agent Universe and open an agent card.
        </div>
      )}

      {datasetId && (
        <div className="grid gap-5 lg:grid-cols-[minmax(0,2.2fr),minmax(0,1.6fr)]">
          <section className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 shadow-sm shadow-slate-950/40">
            <QueryPlayground datasetId={datasetId} onDatasetId={setDatasetId} />
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 shadow-sm shadow-slate-950/40">
            <header className="mb-3 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-slate-50">Taxonomy router</h3>
                <p className="mt-1 text-xs text-slate-400">
                  The YAML below is the routing map your agent uses to validate and back off filters.
                </p>
              </div>
              {taxonomy?.stats && (
                <div className="rounded-full bg-slate-900 px-3 py-1 text-[11px] text-slate-300">
                  {taxonomy.stats.leaf_rows != null && (
                    <>leaf rows: {taxonomy.stats.leaf_rows}</>
                  )}
                </div>
              )}
            </header>

            {loadingTaxonomy && (
              <div className="rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-xs text-slate-300">
                Loading taxonomy…
              </div>
            )}
            {taxonomyError && (
              <div className="rounded-xl border border-red-500/60 bg-red-950/40 px-3 py-2 text-xs text-red-200">
                {taxonomyError}
              </div>
            )}
            {taxonomy && !taxonomyError && (
              <TaxonomyPanel
                yaml={taxonomy.taxonomy_yaml}
                onCopy={() => navigator.clipboard.writeText(taxonomy.taxonomy_yaml)}
              />
            )}
          </section>
        </div>
      )}
    </div>
  );
};

export default AgentDetailPage;
