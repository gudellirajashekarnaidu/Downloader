import { useId } from "react";

const SIZE = 200;
const STROKE = 14;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

/**
 * Circular progress indicator.
 * value: 0 to 1. indeterminate: show a spinning arc instead (we don't know the progress yet).
 * tone: "brand" or "danger".
 */
export default function ProgressRing({ value = 0, indeterminate = false, tone = "brand", children }) {
  const gradientId = useId().replace(/:/g, "");
  const shown = indeterminate ? 0.25 : Math.min(Math.max(value, 0), 1);
  const offset = CIRCUMFERENCE * (1 - shown);
  const stroke = tone === "danger" ? "#C93434" : `url(#${gradientId})`;

  return (
    <div className="relative mx-auto h-[200px] w-[200px]">
      <div className={`h-full w-full ${indeterminate ? "animate-spin motion-reduce:animate-none" : ""}`}>
        <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="h-full w-full -rotate-90" aria-hidden="true">
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#3E91FF" />
              <stop offset="100%" stopColor="#12A8DE" />
            </linearGradient>
          </defs>
          <circle cx={SIZE / 2} cy={SIZE / 2} r={RADIUS} fill="none" stroke="#E6E9EE" strokeWidth={STROKE} />
          {shown > 0 && (
            <circle
              cx={SIZE / 2}
              cy={SIZE / 2}
              r={RADIUS}
              fill="none"
              stroke={stroke}
              strokeWidth={STROKE}
              strokeLinecap="round"
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={offset}
              className="transition-[stroke-dashoffset] duration-300 motion-reduce:transition-none"
            />
          )}
        </svg>
      </div>
      <div className="absolute inset-0 flex flex-col items-center justify-center">{children}</div>
    </div>
  );
}
