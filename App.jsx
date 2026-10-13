import { useEffect, useState } from "react";
import { analyzeLink, createJob, getJob } from "./api.js";
import OptionsCard from "./components/OptionsCard.jsx";
import ProgressCard from "./components/ProgressCard.jsx";
import ResultCard from "./components/ResultCard.jsx";
import SupportedCard from "./components/SupportedCard.jsx";
import UrlCard from "./components/UrlCard.jsx";

export default function App() {
  const [url, setUrl] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");
  const [kind, setKind] = useState("video");
  const [quality, setQuality] = useState("best");
  const [job, setJob] = useState(null);
  const [starting, setStarting] = useState(false);

  async function handleAnalyze() {
    setAnalyzing(true);
    setAnalyzeError("");
    setAnalysis(null);
    setJob(null);
    try {
      const result = await analyzeLink(url.trim());
      setAnalysis(result);
      setKind(result.can_video ? "video" : "audio");
      setQuality("best");
    } catch (error) {
      setAnalyzeError(error.message);
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleDownload() {
    setStarting(true);
    setJob(null);
    try {
      const created = await createJob({
        url: analysis.url,
        kind,
        quality: kind === "video" ? quality : null,
      });
      setJob(created);
    } catch (error) {
      setJob({ id: "", status: "failed", progress: 0, kind, error: error.message });
    } finally {
      setStarting(false);
    }
  }

  // Poll the server while a job is running.
  const jobId = job?.id;
  const jobStatus = job?.status;
  useEffect(() => {
    if (!jobId || (jobStatus !== "queued" && jobStatus !== "working")) return undefined;
    const timer = setInterval(async () => {
      try {
        setJob(await getJob(jobId));
      } catch (error) {
        setJob((current) => ({ ...current, status: "failed", error: error.message }));
      }
    }, 800);
    return () => clearInterval(timer);
  }, [jobId, jobStatus]);

  let phase = "idle";
  if (analyzing) phase = "analyzing";
  else if (starting) phase = "queued";
  else if (job) phase = job.status;

  const busy = starting || phase === "queued" || phase === "working";

  return (
    <div className="mx-auto min-h-screen max-w-5xl px-4 pb-16 pt-14 sm:px-6 sm:pt-24">
      <header className="mb-8 sm:mb-12">
        <h1 className="bg-gradient-to-r from-brand to-brand-cyan bg-clip-text text-5xl font-bold leading-tight tracking-tight text-transparent sm:text-6xl">
          Downloder
        </h1>
        <p className="mt-2 max-w-md text-lg text-muted">Save a video or pull out its audio. Paste a link to start.</p>
      </header>

      <main className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_340px] lg:items-start">
        <div className="flex flex-col gap-4">
          <UrlCard url={url} onChange={setUrl} onAnalyze={handleAnalyze} busy={analyzing} error={analyzeError} />
          {analysis && <ResultCard key={analysis.url} analysis={analysis} />}
          {analysis && (
            <OptionsCard
              analysis={analysis}
              kind={kind}
              onKind={setKind}
              quality={quality}
              onQuality={setQuality}
              onDownload={handleDownload}
              busy={busy}
            />
          )}
        </div>

        <div className="flex flex-col gap-4 lg:sticky lg:top-6">
          <ProgressCard phase={phase} job={job} kind={kind} />
          <SupportedCard />
        </div>
      </main>

      <footer className="mt-10 text-sm text-muted">Only save media you own or have permission to download.</footer>
    </div>
  );
}
