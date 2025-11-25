import React, { useState } from "react";
import { Link, Route, Routes } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import ConfigPage from "./pages/ConfigPage";
import EtlPage from "./pages/EtlPage";
import TaxonomyPage from "./pages/TaxonomyPage";
import QueryPlayground from "./pages/QueryPlayground";
import AgentUniversePage from "./pages/AgentUniversePage";
import AgentBuilderPage from "./pages/AgentBuilderPage";
import AgentDetailPage from "./pages/AgentDetailPage";

const App: React.FC = () => {
  const [datasetId, setDatasetId] = useState("");

  return (
    <div className="min-h-screen bg-background text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-6">
        <header className="mb-8 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-accent/15 text-sm font-semibold text-accent shadow-lg shadow-sky-500/30">
              AS
            </span>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">Agent Studio</h1>
              <p className="text-xs text-slate-400">Build and explore data-grounded agents.</p>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <Link
              to="/agents/new"
              className="inline-flex items-center gap-1 rounded-full bg-accent px-3 py-1.5 text-xs font-medium text-slate-950 shadow-sm shadow-sky-500/40 hover:bg-sky-300 transition-colors"
            >
              <span className="text-base leading-none">＋</span>
              New agent from data
            </Link>
            {datasetId && (
              <div className="hidden items-center gap-2 rounded-full border border-slate-700 bg-slate-900/60 px-3 py-1 text-[11px] text-slate-300 sm:flex">
                <span className="text-slate-500">Active dataset</span>
                <code className="truncate font-mono text-[11px] text-slate-100">{datasetId}</code>
              </div>
            )}
          </div>
        </header>

        <main className="mb-6 flex-1">
          <Routes>
            <Route path="/" element={<AgentUniversePage />} />
            <Route path="/agents/new" element={<AgentBuilderPage datasetId={datasetId} onDatasetId={setDatasetId} />} />
            <Route path="/agents/:datasetId" element={<AgentDetailPage onDatasetId={setDatasetId} />} />

            {/* Legacy direct-step flows remain available for now */}
            <Route path="/upload" element={<UploadPage datasetId={datasetId} onDatasetId={setDatasetId} />} />
            <Route path="/config" element={<ConfigPage datasetId={datasetId} onDatasetId={setDatasetId} />} />
            <Route path="/etl" element={<EtlPage datasetId={datasetId} onDatasetId={setDatasetId} />} />
            <Route path="/taxonomy" element={<TaxonomyPage datasetId={datasetId} onDatasetId={setDatasetId} />} />
            <Route path="/query" element={<QueryPlayground datasetId={datasetId} onDatasetId={setDatasetId} />} />
          </Routes>
        </main>

        <footer className="mt-auto border-t border-slate-800/70 pt-4 text-xs text-slate-500">
          <span>Made for MCP data agents ·</span>{" "}
          <span className="text-slate-400">upload · configure · route · query.</span>
        </footer>
      </div>
    </div>
  );
};

export default App;
