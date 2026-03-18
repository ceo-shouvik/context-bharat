/**
 * Feature cards — shows available developer tools on the dashboard.
 * Client component because it reads runtime feature flags.
 */
"use client";

import Link from "next/link";
import { features } from "@/lib/features";

interface FeatureCard {
  title: string;
  description: string;
  href: string;
  enabled: boolean;
}

const allFeatures: FeatureCard[] = [
  {
    title: "Integration Cookbooks",
    description: "Step-by-step guides combining multiple Indian APIs into real integrations.",
    href: "/cookbooks",
    enabled: features.cookbooks,
  },
  {
    title: "Framework Starters",
    description: "Production-ready starter templates for Next.js, Django, FastAPI, and more.",
    href: "/starters",
    enabled: features.frameworkStarters,
  },
  {
    title: "Developer Tools",
    description: "Generate code snippets, tests, OpenAPI specs, and SDKs for any library.",
    href: "/tools",
    enabled:
      features.codeSnippets ||
      features.testGeneration ||
      features.openapiGeneration ||
      features.sdkGeneration,
  },
  {
    title: "Compliance Guide",
    description: "Regulatory requirements and checklists for Indian fintech and government APIs.",
    href: "/compliance",
    enabled: features.complianceLayer,
  },
  {
    title: "Community Q&A",
    description: "Ask questions and share knowledge about Indian API integrations.",
    href: "/community",
    enabled: features.communityQa,
  },
];

export function FeatureCards() {
  const visibleFeatures = allFeatures.filter((f) => f.enabled);

  if (visibleFeatures.length === 0) return null;

  return (
    <section>
      <h2 className="text-white font-semibold mb-4">Features</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {visibleFeatures.map((feature) => (
          <Link
            key={feature.href}
            href={feature.href}
            className="bg-[#0c1120] border border-[#1e2d44] rounded-xl p-5 hover:border-[#f59e1c]/50 transition-colors group"
          >
            <h3 className="text-white font-medium mb-1 group-hover:text-[#f59e1c] transition-colors">
              {feature.title}
            </h3>
            <p className="text-gray-400 text-sm">{feature.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
