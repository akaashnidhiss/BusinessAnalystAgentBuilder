import React from "react";

type Props = {
  rows: Record<string, unknown>[];
};

const ResultsTable: React.FC<Props> = ({ rows }) => {
  if (!rows.length) {
    return <p className="text-[11px] text-slate-500">No results yet. Run a query to see rows here.</p>;
  }

  const columns = Object.keys(rows[0]);
  return (
    <div className="max-h-64 overflow-auto rounded-lg border border-slate-800 bg-slate-950/80">
      <table className="min-w-full border-collapse text-xs">
        <thead className="bg-slate-900/80">
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                className="sticky top-0 border-b border-slate-800 px-3 py-2 text-left font-medium text-slate-300"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? "bg-slate-950/80" : "bg-slate-950/40"}>
              {columns.map((col) => (
                <td key={col} className="border-b border-slate-900 px-3 py-1.5 text-slate-100">
                  {String(row[col] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
