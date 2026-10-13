import { useState } from "react";
import { formatDuration, formatSize } from "../format.js";
import { PlayIcon } from "./Icons.jsx";

export default function ResultCard({ analysis }) {
  const [thumbFailed, setThumbFailed] = useState(false);
  const details = [formatDuration(analysis.duration), formatSize(analysis.size_bytes), analysis.uploader].filter(Boolean);

  return (
    <section className="flex items-center gap-4 rounded-card bg-surface p-4 shadow-card sm:p-5">
      <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-canvas text-muted">
        {analysis.thumbnail && !thumbFailed ? (
          <img
            src={analysis.thumbnail}
            alt=""
            referrerPolicy="no-referrer"
            onError={() => setThumbFailed(true)}
            className="h-full w-full object-cover"
          />
        ) : (
          <PlayIcon className="h-7 w-7" />
        )}
      </div>
      <div className="min-w-0">
        <h2 className="line-clamp-2 text-base font-semibold leading-snug">{analysis.title}</h2>
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
          <span className="rounded-full bg-brand/10 px-2.5 py-0.5 font-semibold text-brand">{analysis.platform}</span>
          {details.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </div>
    </section>
  );
}
