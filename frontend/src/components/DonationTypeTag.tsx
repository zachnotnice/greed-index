import clsx from "clsx";

const TYPE_CONFIG: Record<string, { label: string; color: string; loophole: boolean }> = {
  direct_grant: { label: "Direct Grant", color: "bg-green-900/50 text-green-300 border-green-700/50", loophole: false },
  foundation: { label: "Foundation", color: "bg-blue-900/50 text-blue-300 border-blue-700/50", loophole: false },
  donor_advised_fund: { label: "DAF ⚠️", color: "bg-yellow-900/50 text-yellow-300 border-yellow-700/50", loophole: true },
  charitable_llc: { label: "Charitable LLC ✗", color: "bg-red-900/50 text-red-300 border-red-700/50", loophole: true },
  conservation_easement: { label: "Easement ✗", color: "bg-red-900/50 text-red-300 border-red-700/50", loophole: true },
  naming_rights: { label: "Naming Rights ⚠️", color: "bg-orange-900/50 text-orange-300 border-orange-700/50", loophole: true },
  political: { label: "Political ✗", color: "bg-purple-900/50 text-purple-300 border-purple-700/50", loophole: true },
  giving_pledge: { label: "Pledge Only ✗", color: "bg-gray-900/50 text-gray-400 border-gray-700/50", loophole: true },
  in_kind: { label: "In-Kind", color: "bg-slate-900/50 text-slate-300 border-slate-700/50", loophole: false },
  impact_investment: { label: "Impact Investment ⚠️", color: "bg-amber-900/50 text-amber-300 border-amber-700/50", loophole: true },
};

export default function DonationTypeTag({ type }: { type: string }) {
  const config = TYPE_CONFIG[type] || { label: type, color: "bg-white/10 text-white/60 border-white/10", loophole: false };
  return (
    <span className={clsx("text-xs px-2 py-0.5 rounded border font-medium", config.color)}>
      {config.label}
    </span>
  );
}
