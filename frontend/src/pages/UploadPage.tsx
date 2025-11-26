import React, { useState } from "react";
import { DEFAULT_USER_ID, apiUrl } from "../api";

type Props = {
  datasetId?: string;
  onDatasetId?: (id: string) => void;
  uploadId?: string | null;
  onUploadId?: (id: string) => void;
};

const UploadPage: React.FC<Props> = ({ datasetId, uploadId: initialUploadId, onUploadId }) => {
  const [uploadId, setUploadId] = useState<string | null>(initialUploadId || null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (evt: React.ChangeEvent<HTMLInputElement>) => {
    const file = evt.target.files?.[0];
    if (!file) return;
    setError(null);
    const fd = new FormData();
    fd.append("file", file);
    setIsUploading(true);
    setStatus("Uploading and generating preview…");
    try {
      const res = await fetch(
        apiUrl(`/api/users/${DEFAULT_USER_ID}/datasets/preview`),
        { method: "POST", body: fd },
      );
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Upload failed");
      }
      const json = await res.json();
      setUploadId(json.upload_id);
      onUploadId?.(json.upload_id);
      setStatus(
        `Previewed ${file.name}. Use the next step to choose schema and create the dataset.`
      );
    } catch (e: any) {
      setError(e?.message || "Upload failed");
      setStatus("");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-slate-50">Upload dataset</h3>
      <p className="text-xs text-slate-400">
        Start with a CSV export from your warehouse or operational system. We will only read a small preview for
        schema inference.
      </p>
      <label className="block">
        <span className="text-xs font-medium uppercase tracking-[0.16em] text-slate-400">CSV file</span>
        <div className="mt-2 flex items-center gap-3 rounded-xl border border-dashed border-slate-600 bg-slate-950/80 px-4 py-3">
          <input
            type="file"
            accept=".csv"
            onChange={handleUpload}
            className="block w-full text-xs text-slate-200 file:mr-4 file:rounded-md file:border-0 file:bg-slate-200 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-slate-900 hover:file:bg-white/90"
          />
        </div>
      </label>
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
      {uploadId && (
        <div className="flex items-center gap-2 text-[11px] text-slate-300">
          <span className="text-slate-400">upload_id</span>
          <code className="rounded bg-slate-900 px-2 py-0.5 font-mono text-[11px] text-slate-100">
            {uploadId}
          </code>
        </div>
      )}
      {isUploading && (
        <div className="text-[11px] text-slate-400">Uploading… this may take a moment for large files.</div>
      )}
    </div>
  );
};

export default UploadPage;
