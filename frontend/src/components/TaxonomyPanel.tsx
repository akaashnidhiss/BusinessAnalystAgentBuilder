import React from "react";

type Props = {
  yaml: string;
  onCopy?: () => void;
};

const TaxonomyPanel: React.FC<Props> = ({ yaml, onCopy }) => {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-950/80 p-3 text-xs text-slate-200">
      <header className="mb-2 flex items-center justify-between gap-2">
        <strong className="text-xs font-semibold text-slate-100">Taxonomy (router)</strong>
        <button
          type="button"
          onClick={onCopy}
          className="rounded-full border border-slate-600 bg-slate-900 px-2 py-0.5 text-[11px] font-medium text-slate-200 hover:border-accent hover:text-accent transition-colors"
        >
          Copy YAML
        </button>
      </header>
      <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-950/90 p-2 font-mono text-[11px] text-slate-100">
        {yaml}
      </pre>
    </section>
  );
};

export default TaxonomyPanel;
