import React from "react";

type Props = {
  datasetId?: string;
  onDatasetId?: (id: string) => void;
};

const EtlPage: React.FC<Props> = ({ datasetId }) => {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-50">ETL + DuckDB initialization</h3>
      <p className="text-xs text-slate-400">
        Normalize the dataset, build a leaf index for all valid filter combinations, render the taxonomy YAML, and load
        the normalized data into an in-memory DuckDB table. This now happens automatically as part of dataset creation.
        Once configuration is saved, your dataset is ready for taxonomy inspection and querying.
      </p>
      {datasetId && (
        <div className="rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-[11px] text-slate-300">
          <p className="font-medium text-slate-200">Current dataset</p>
          <code className="mt-1 block truncate font-mono text-[11px] text-slate-100">{datasetId}</code>
        </div>
      )}
    </div>
  );
};

export default EtlPage;
