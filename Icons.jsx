const icon = (children, extra = {}) =>
  function Icon({ className = "h-5 w-5" }) {
    return (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={className}
        aria-hidden="true"
        {...extra}
      >
        {children}
      </svg>
    );
  };

export const DownloadIcon = icon(<path d="M12 4v11m0 0-4-4m4 4 4-4M5 20h14" />);
export const LinkIcon = icon(
  <path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 0 0-5.66-5.66l-1 1M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1-1" />
);
export const VideoIcon = icon(
  <>
    <rect x="3" y="6" width="13" height="12" rx="3" />
    <path d="m16 10 5-3v10l-5-3" />
  </>
);
export const AudioIcon = icon(
  <>
    <path d="M9 18V6l10-2v12" />
    <circle cx="6" cy="18" r="3" />
    <circle cx="16" cy="16" r="3" />
  </>
);
export const CheckIcon = icon(<path d="m5 12.5 4.5 4.5L19 7.5" />);
export const AlertIcon = icon(
  <>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 8v5M12 16.5v.5" />
  </>
);
export const PlayIcon = icon(<path d="M8 5.5v13l11-6.5z" />);
export const CameraIcon = icon(
  <>
    <rect x="3" y="3" width="18" height="18" rx="5" />
    <circle cx="12" cy="12" r="4" />
    <path d="M17.5 6.5h.01" />
  </>
);
export const CrossIcon = icon(<path d="M5 5l14 14M19 5 5 19" />);
export const PlaneIcon = icon(
  <>
    <path d="M22 2 11 13" />
    <path d="M22 2 15 22l-4-9-9-4z" />
  </>
);
