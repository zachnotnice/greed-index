"use client";

import { useState } from "react";

// Small client component for the "Copy Link" action. The profile page is a
// server component, so it can't attach an onClick handler directly.
export default function CopyLinkButton() {
  const [copied, setCopied] = useState(false);

  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(window.location.href);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="bg-white/10 hover:bg-white/20 text-white px-4 py-2 rounded-lg text-sm transition-colors"
    >
      {copied ? "Copied!" : "Copy Link"}
    </button>
  );
}
