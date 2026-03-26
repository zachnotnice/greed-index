import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Methodology | Greed Index",
  description: "Full transparency on how Greed Index scores are calculated. Data sources, loophole criteria, scoring algorithm.",
};

export default function MethodologyPage() {
  return (
    <main className="max-w-3xl mx-auto px-4 sm:px-6 py-12">
      <h1 className="text-4xl font-black mb-2">Methodology</h1>
      <p className="text-white/40 mb-10">
        Every score on this site is fully explainable. Here&apos;s exactly how we calculate it.
      </p>

      <section className="space-y-10">
        <div>
          <h2 className="text-2xl font-bold mb-3 text-red-400">Data Sources</h2>
          <ul className="text-white/60 space-y-2 text-sm leading-relaxed list-disc list-inside">
            <li><strong className="text-white">Net Worth:</strong> Forbes Billionaires list, Bloomberg Billionaires Index (publicly available data)</li>
            <li><strong className="text-white">Charitable Giving:</strong> IRS Form 990 filings via ProPublica Nonprofit Explorer (free public database)</li>
            <li><strong className="text-white">Foundation Data:</strong> IRS 990-PF filings, Charity Navigator ratings</li>
            <li><strong className="text-white">Giving Pledge:</strong> Official Giving Pledge website (pledges are public)</li>
            <li><strong className="text-white">Wealth Growth:</strong> Historical Forbes data, public company filings</li>
          </ul>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-3 text-red-400">What Counts as a Loophole</h2>
          <p className="text-white/50 text-sm mb-4">
            Not all &quot;charitable&quot; giving is equal. These structures are flagged as loopholes — either partially or fully — because they provide tax benefits without requiring genuine social benefit.
          </p>
          <div className="space-y-4">
            {[
              {
                type: "Donor-Advised Funds (DAFs)",
                penalty: "50% discount",
                why: "The donor gets an immediate tax deduction but the money can sit in the fund indefinitely. The IRS imposes no minimum payout requirement. Funds often grow tax-free while society waits for the giving to happen.",
              },
              {
                type: "Charitable LLCs",
                penalty: "100% excluded",
                why: "Structures like the Chan Zuckerberg Initiative are LLCs, not 501(c)(3)s. They face no transparency requirements, no mandatory payout, and the donor retains full control of assets and investments. They are investment vehicles with a charitable marketing veneer.",
              },
              {
                type: "Conservation Easements",
                penalty: "100% excluded",
                why: "Easements on personal property are a well-documented IRS abuse. The donor retains full use of the land while claiming a deduction based on an inflated appraisal of what they 'gave up.' The Treasury and IRS have flagged these as abusive tax shelters.",
              },
              {
                type: "Naming Rights Donations",
                penalty: "40% discount",
                why: "Donating $400M to get a business school named after you provides personal commercial value — brand building, prestige, reputation management. A portion of the donation is attributed to this personal benefit and excluded from the genuine giving calculation.",
              },
              {
                type: "Political 'Charity'",
                penalty: "80% excluded",
                why: "501(c)(4)s and political foundations that advance the donor's business or political interests are not philanthropy. Americans for Prosperity, the Cato Institute, and similar organizations are primarily mechanisms for political influence, not social benefit.",
              },
              {
                type: "Giving Pledge Signatures",
                penalty: "100% excluded (until actual transfer)",
                why: "The Giving Pledge is a voluntary, non-binding commitment. Signing it costs nothing and carries no legal obligation. We give no credit for pledges — only for documented asset transfers.",
              },
              {
                type: "Excessive Foundation Overhead",
                penalty: "Proportional, above 20% threshold",
                why: "Private foundations that spend more than 20% of expenses on administrative costs — especially family salaries and executive pay — are penalized proportionally. The IRS requires only 5% annual payout; foundations at exactly 5% receive an additional penalty.",
              },
            ].map((item) => (
              <div key={item.type} className="border border-white/10 rounded-xl p-4">
                <div className="flex items-center gap-3 mb-2">
                  <span className="font-semibold text-white">{item.type}</span>
                  <span className="text-xs px-2 py-0.5 bg-red-900/30 text-red-400 rounded border border-red-700/30">
                    {item.penalty}
                  </span>
                </div>
                <p className="text-white/50 text-sm leading-relaxed">{item.why}</p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-3 text-red-400">Scoring Formula</h2>
          <div className="bg-black/40 border border-white/10 rounded-xl p-6 font-mono text-sm space-y-2 text-white/70">
            <p><span className="text-white">Step 1:</span> adjusted_giving = Σ (donation × genuine_fraction)</p>
            <p><span className="text-white">Step 2:</span> giving_ratio = adjusted_giving / net_worth</p>
            <p><span className="text-white">Step 3:</span> giving_component = 100 − log₁₀(ratio + 0.001) × 20 × (65%)</p>
            <p><span className="text-white">Step 4:</span> quality_component = cause quality × (20%)</p>
            <p><span className="text-white">Step 5:</span> wealth_penalty = (wealth_growth − giving_growth) / 10 × (15%)</p>
            <p><span className="text-white">Step 6:</span> pledge_penalty = +5 if pledge signed but not honored</p>
            <p className="border-t border-white/10 pt-2"><span className="text-red-400 font-bold">Greed Score</span> = normalize(steps 3–6) to 0–100</p>
          </div>
          <p className="text-white/30 text-sm mt-3">
            Scores are normalized across all billionaires so the full 0–100 range is used. This means scores are relative — a score reflects how a billionaire compares to all others in the index, not an absolute giving threshold.
          </p>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-3 text-red-400">Cause Quality Multipliers</h2>
          <p className="text-white/50 text-sm mb-3">
            Not all giving has equal impact. We apply multipliers to account for the effectiveness and reach of different cause areas, based on GiveWell, WHO, and development economics research.
          </p>
          <div className="grid grid-cols-3 gap-3 text-sm">
            {[
              { tier: "High Impact", modifier: "1.2×", causes: "Global health, poverty, hunger, pandemic prevention, climate" },
              { tier: "Medium Impact", modifier: "1.0×", causes: "Education, housing, criminal justice, mental health, veterans" },
              { tier: "Lower Impact", modifier: "0.8×", causes: "Arts, elite universities, hospitals, religious organizations" },
            ].map((row) => (
              <div key={row.tier} className="bg-white/5 border border-white/10 rounded-xl p-4">
                <div className="font-bold text-white">{row.tier}</div>
                <div className="text-green-400 font-mono font-bold">{row.modifier}</div>
                <div className="text-white/40 text-xs mt-1">{row.causes}</div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-3 text-red-400">Dispute & Update Process</h2>
          <p className="text-white/50 text-sm leading-relaxed">
            If you believe a score is incorrect or have documentation of giving not reflected here,{" "}
            <a href="https://github.com" className="text-red-400 hover:text-red-300 underline">
              submit a correction via GitHub
            </a>
            . All data is version-controlled and changes are documented with sources. We aim to respond within 14 days.
          </p>
          <p className="text-white/30 text-xs mt-3">
            Entries marked &quot;Estimated&quot; use publicly reported figures but have not been directly verified against IRS filings. Entries marked &quot;Verified&quot; have been confirmed against Form 990 or official press releases.
          </p>
        </div>
      </section>
    </main>
  );
}
