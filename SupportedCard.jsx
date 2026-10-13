import { CameraIcon, CrossIcon, LinkIcon, PlaneIcon } from "./Icons.jsx";

const SOURCES = [
  { name: "Instagram", note: "Public posts and Reels", Icon: CameraIcon, tint: "bg-pink-100 text-pink-700" },
  { name: "X", note: "Public posts with video", Icon: CrossIcon, tint: "bg-slate-200 text-slate-800" },
  { name: "Telegram", note: "Public channel posts", Icon: PlaneIcon, tint: "bg-sky-100 text-sky-700" },
  { name: "Direct links", note: "Files ending in .mp4, .webm, .mp3 and similar", Icon: LinkIcon, tint: "bg-blue-100 text-blue-700" },
];

export default function SupportedCard() {
  return (
    <section className="rounded-card bg-surface p-5 shadow-card sm:p-6">
      <h2 className="text-lg font-semibold">Supported links</h2>
      <ul className="mt-2">
        {SOURCES.map(({ name, note, Icon, tint }) => (
          <li key={name} className="flex items-center gap-4 border-t border-track py-3.5 first:border-t-0">
            <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${tint}`}>
              <Icon className="h-5 w-5" />
            </span>
            <span className="min-w-0">
              <span className="block text-base font-semibold">{name}</span>
              <span className="block text-sm text-muted">{note}</span>
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-sm text-muted">
        Private posts and anything behind a login can't be saved. WhatsApp doesn't offer public links to videos.
      </p>
    </section>
  );
}
