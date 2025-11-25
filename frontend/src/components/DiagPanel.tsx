import React from "react";

type Props = {
  backoffLevel?: string | null;
  reason?: string | null;
  canonical?: Record<string, string[]>;
  counts?: Record<string, number>;
};

const DiagPanel: React.FC<Props> = ({ backoffLevel, reason, canonical, counts }) => {
  return (
    <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950/80 p-3 text-xs text-slate-200">
      <div className="mb-1 flex items-center justify-between gap-2">
        <strong className="text-xs font-semibold text-slate-100">Diagnostics</strong>
        <span className="rounded-full bg-slate-900 px-2 py-0.5 text-[10px] text-slate-400">
          {backoffLevel || "no-backoff"}
        </span>
      </div>
      <div className="mb-1 text-[11px] text-slate-400">
        Backoff level: <span className="text-slate-200">{backoffLevel || "n/a"}</span>
      </div>
      <div className="mb-2 text-[11px] text-slate-400">
        Reason: <span className="text-slate-200">{reason || "n/a"}</span>
      </div>
      {canonical && (
        <div className="mt-2">
          <div className="mb-1 text-[11px] font-medium text-slate-300">Canonical filters used</div>
          <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-950/80 p-2 font-mono text-[11px] text-slate-100">
            {JSON.stringify(canonical, null, 2)}
          </pre>
        </div>
      )}
      {counts && (
        <div className="mt-2">
          <div className="mb-1 text-[11px] font-medium text-slate-300">Counts</div>
          <pre className="whitespace-pre-wrap rounded-lg bg-slate-950/80 p-2 font-mono text-[11px] text-slate-100">
            {JSON.stringify(counts, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default DiagPanel;
