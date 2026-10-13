import { LinkIcon } from "./Icons.jsx";

export default function UrlCard({ url, onChange, onAnalyze, busy, error }) {
  async function paste() {
    try {
      const text = await navigator.clipboard.readText();
      if (text) onChange(text.trim());
    } catch {
      /* Clipboard access was declined. The person can still paste into the box. */
    }
  }

  return (
    <section className="rounded-card bg-surface p-5 shadow-card sm:p-6">
      <form
        noValidate
        onSubmit={(event) => {
          event.preventDefault();
          onAnalyze();
        }}
      >
        <label htmlFor="media-url" className="mb-3 block text-base font-semibold">
          Video link
        </label>
        <div className="flex items-center gap-2 rounded-2xl bg-canvas pl-4 pr-2 focus-within:ring-2 focus-within:ring-brand-light">
          <LinkIcon className="h-5 w-5 shrink-0 text-muted" />
          <input
            id="media-url"
            type="url"
            inputMode="url"
            autoComplete="off"
            spellCheck="false"
            value={url}
            onChange={(event) => onChange(event.target.value)}
            placeholder="Paste a video link"
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "media-url-error" : undefined}
            className="min-w-0 flex-1 bg-transparent py-4 text-base placeholder:text-muted focus-visible:outline-none"
          />
          <button
            type="button"
            onClick={paste}
            className="rounded-full px-4 py-2 text-sm font-semibold text-brand hover:bg-brand/10"
          >
            Paste
          </button>
        </div>

        {error && (
          <p id="media-url-error" role="alert" className="mt-3 text-sm text-danger">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={busy || !url.trim()}
          className="mt-4 w-full rounded-full bg-brand py-3.5 text-base font-semibold text-white transition-opacity disabled:opacity-50"
        >
          {busy ? "Analyzing…" : "Analyze link"}
        </button>
      </form>
    </section>
  );
}
