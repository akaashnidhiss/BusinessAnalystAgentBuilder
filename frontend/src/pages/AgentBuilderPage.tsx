import React, { useState } from "react";
import UploadPage from "./UploadPage";
import ConfigPage from "./ConfigPage";
import EtlPage from "./EtlPage";
import TaxonomyPage from "./TaxonomyPage";
import QueryPlayground from "./QueryPlayground";

type Props = {
  datasetId?: string;
  onDatasetId?: (id: string) => void;
  uploadId?: string | null;
  onUploadId?: (id: string) => void;
};

const steps = [
  {
    id: 1,
    title: "Upload data",
    description: "Start from a CSV or table export.",
  },
  {
    id: 2,
    title: "Choose schema",
    description: "Mark filter dimensions and metrics.",
  },
  {
    id: 3,
    title: "Generate taxonomy",
    description: "Normalize, index and build the router.",
  },
  {
    id: 4,
    title: "Test the agent",
    description: "Run a few queries and inspect diagnostics.",
  },
];

const AgentBuilderPage: React.FC<Props> = ({ datasetId, onDatasetId, uploadId, onUploadId }) => {
  const [currentStep, setCurrentStep] = useState<number>(1);

  const activeStep = steps.find((s) => s.id === currentStep) ?? steps[0];

  return (
    <div className="grid gap-6 md:grid-cols-[260px,minmax(0,1fr)]">
      <aside className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4 shadow-inner shadow-slate-950/60">
        <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Agent builder</h2>
        <p className="mt-1 text-xs text-slate-500">
          Move from raw data to a taxonomy-backed agent in four guided steps.
        </p>
        <ol className="mt-4 space-y-3 text-sm">
          {steps.map((step) => {
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;
            return (
              <li key={step.id}>
                <button
                  type="button"
                  onClick={() => setCurrentStep(step.id)}
                  className={[
                    "flex w-full items-start gap-3 rounded-xl border px-3 py-2.5 text-left transition-colors",
                    isActive
                      ? "border-accent/80 bg-slate-900/90"
                      : "border-slate-800 bg-slate-950/70 hover:border-slate-600",
                  ].join(" ")}
                >
                  <span
                    className={[
                      "mt-0.5 flex h-5 w-5 items-center justify-center rounded-full border text-[10px] font-medium",
                      isActive
                        ? "border-accent bg-accent/20 text-accent"
                        : isCompleted
                        ? "border-emerald-500/80 bg-emerald-500/15 text-emerald-300"
                        : "border-slate-700 bg-slate-900 text-slate-400",
                    ].join(" ")}
                  >
                    {isCompleted ? "✓" : step.id}
                  </span>
                  <div>
                    <div className="text-xs font-semibold text-slate-100">{step.title}</div>
                    <div className="text-[11px] text-slate-500">{step.description}</div>
                  </div>
                </button>
              </li>
            );
          })}
        </ol>
        {datasetId && (
          <div className="mt-4 rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-[11px] text-slate-400">
            <p className="font-medium text-slate-200">Current dataset</p>
            <code className="mt-1 block truncate font-mono text-[11px] text-slate-100">{datasetId}</code>
          </div>
        )}
      </aside>

      <section className="rounded-2xl border border-slate-800 bg-slate-950/70 p-5 shadow-lg shadow-slate-950/40">
        <header className="mb-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Step {activeStep.id}</p>
            <h2 className="mt-1 text-lg font-semibold text-slate-50">{activeStep.title}</h2>
            <p className="mt-1 text-xs text-slate-400">{activeStep.description}</p>
          </div>
          <div className="hidden text-right text-[11px] text-slate-500 md:block">
            <p className="font-medium text-slate-300">Flow</p>
            <p>Upload → Schema → Taxonomy → Query</p>
          </div>
        </header>

        <div className="space-y-6">
          {currentStep === 1 && (
            <UploadPage
              datasetId={datasetId}
              uploadId={uploadId}
              onUploadId={onUploadId}
              onDatasetId={onDatasetId}
            />
          )}
          {currentStep === 2 && (
            <ConfigPage datasetId={datasetId} onDatasetId={onDatasetId} uploadId={uploadId} />
          )}
          {currentStep === 3 && (
            <div className="space-y-6">
              <EtlPage datasetId={datasetId} onDatasetId={onDatasetId} />
              <div className="border-t border-slate-800 pt-4">
                <TaxonomyPage datasetId={datasetId} onDatasetId={onDatasetId} />
              </div>
            </div>
          )}
          {currentStep === 4 && (
            <QueryPlayground datasetId={datasetId} onDatasetId={onDatasetId} />
          )}
        </div>

        <div className="mt-6 flex items-center justify-between border-t border-slate-800 pt-4 text-xs text-slate-400">
          <span>
            You can jump between steps at any time — just ensure ETL plus DuckDB init ran successfully before heavy
            querying.
          </span>
          <div className="hidden gap-2 md:flex">
            <button
              type="button"
              disabled={currentStep === 1}
              onClick={() => setCurrentStep((s) => Math.max(1, s - 1))}
              className="rounded-full border border-slate-700 bg-slate-950 px-3 py-1 text-[11px] font-medium text-slate-200 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={currentStep === steps.length}
              onClick={() => setCurrentStep((s) => Math.min(steps.length, s + 1))}
              className="rounded-full bg-accent px-3 py-1 text-[11px] font-semibold text-slate-950 shadow-sm shadow-sky-500/50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AgentBuilderPage;
