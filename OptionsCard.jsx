import { AudioIcon, VideoIcon } from "./Icons.jsx";

function Row({ label, children }) {
  return (
    <div className="flex items-center justify-between gap-4 border-t border-track py-4">
      <span className="text-base">{label}</span>
      {children}
    </div>
  );
}

export default function OptionsCard({ analysis, kind, onKind, quality, onQuality, onDownload, busy }) {
  const isVideo = kind === "video";
  const options = [
    { id: "video", label: "Video", Icon: VideoIcon, enabled: analysis.can_video },
    { id: "audio", label: "Audio", Icon: AudioIcon, enabled: analysis.can_audio },
  ];

  return (
    <section className="rounded-card bg-surface p-5 shadow-card sm:p-6">
      <div role="radiogroup" aria-label="What to save" className="grid grid-cols-2 gap-1 rounded-full bg-canvas p-1">
        {options.map(({ id, label, Icon, enabled }) => {
          const selected = kind === id;
          return (
            <button
              key={id}
              type="button"
              role="radio"
              aria-checked={selected}
              disabled={!enabled || busy}
              onClick={() => onKind(id)}
              className={`flex items-center justify-center gap-2 rounded-full py-2.5 text-base font-semibold transition-colors disabled:opacity-40 ${
                selected ? "bg-surface text-brand shadow-card" : "text-muted"
              }`}
            >
              <Icon className="h-5 w-5" />
              {label}
            </button>
          );
        })}
      </div>

      <div className="mt-3">
        <Row label="Format">
          <span className="text-base font-semibold">{isVideo ? "MP4" : "MP3"}</span>
        </Row>
        <Row label="Quality">
          {isVideo && analysis.qualities.length > 0 ? (
            <select
              aria-label="Video quality"
              value={quality}
              disabled={busy}
              onChange={(event) => onQuality(event.target.value)}
              className="rounded-full bg-canvas px-4 py-2 text-base font-semibold"
            >
              <option value="best">Best available</option>
              {analysis.qualities.map((height) => (
                <option key={height} value={String(height)}>
                  {height}p
                </option>
              ))}
            </select>
          ) : (
            <span className="text-base font-semibold">{isVideo ? "Original" : "192 kbps"}</span>
          )}
        </Row>
      </div>

      <button
        type="button"
        onClick={onDownload}
        disabled={busy || (isVideo ? !analysis.can_video : !analysis.can_audio)}
        className="mt-2 w-full rounded-full bg-brand py-3.5 text-base font-semibold text-white transition-opacity disabled:opacity-50"
      >
        {isVideo ? "Download video" : "Extract audio"}
      </button>
    </section>
  );
}
