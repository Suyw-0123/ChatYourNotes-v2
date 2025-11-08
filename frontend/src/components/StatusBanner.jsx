import { useEffect } from "react";

const AUTO_DISMISS_MS = 4000;

export default function StatusBanner({ message, tone, onDismiss }) {
  useEffect(() => {
    if (!message) return;

    const timer = setTimeout(() => {
      onDismiss();
    }, AUTO_DISMISS_MS);

    return () => clearTimeout(timer);
  }, [message, onDismiss]);

  if (!message) {
    return null;
  }

  return (
    <div className={`status-banner ${tone}`} role="status">
      <span>{message}</span>
      <button type="button" onClick={onDismiss}>
        ×
      </button>
    </div>
  );
}
