import { fileUrl } from "../api.js";
import { AlertIcon, CheckIcon, DownloadIcon } from "./Icons.jsx";
import ProgressRing from "./ProgressRing.jsx";

/**
 * phase: idle | analyzing | queued | working | done | failed
 */
export default function ProgressCard({ phase, job, kind }) {
  const percent = Math.round((job?.progress ?? 0) * 100);
  const waiting = phase === "analyzing" || phase === "queued" || (phase === "working" && percent === 0);

  let ringValue = 0;
  if (phase === "working") ringValue = job.progress;
  if (phase === "done" || phase === "failed") ringValue = 1;

  let centre = (
    <>
      <DownloadIcon className="h-9 w-9 text-brand" />
      <span className="mt-1 text-base font-semibold">Ready</span>
    </>
  );
  if (waiting) centre = <span className="text-base font-semibold text-muted">Working</span>;
  if (phase === "working" && percent > 0) centre = <span className="text-4xl font-bold">{percent}%</span>;
  if (phase === "done") centre = <CheckIcon className="h-12 w-12 text-brand" />;
  if (phase === "failed") centre = <AlertIcon className="h-12 w-12 text-danger" />;

  const titles = {
    idle: "Nothing to save yet",
    analyzing: "Checking the link",
    queued: "Starting",
    working: kind === "audio" ? "Extracting audio" : "Downloading video",
    done: "Ready to save",
    failed: "Couldn't finish",
  };
  const notes = {
    idle: "Analyze a link to get started.",
    analyzing: "This usually takes a few seconds.",
    queued: "Your request is in line.",
    working: "Keep this page open.",
    done: job?.filename,
    failed: job?.error,
  };

  return (
    <section className="rounded-card bg-surface p-6 shadow-card">
      <ProgressRing value={ringValue} indeterminate={waiting} tone={phase === "failed" ? "danger" : "brand"}>
        {centre}
      </ProgressRing>

      <div className="mt-5 text-center" aria-live="polite">
        <h2 className="text-lg font-semibold">{titles[phase]}</h2>
        <p className="mt-1 break-words text-sm text-muted">{notes[phase]}</p>
      </div>

      {phase === "done" && job.download_url && (
        <a
          href={fileUrl(job.download_url)}
          download
          className="mt-5 flex w-full items-center justify-center rounded-full bg-brand py-3.5 text-base font-semibold text-white"
        >
          Save file
        </a>
      )}
    </section>
  );
}
