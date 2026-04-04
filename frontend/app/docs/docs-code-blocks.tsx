/**
 * DocsCodeBlocks — client wrappers for code blocks on the docs page.
 * Separated because the docs page is a Server Component but CodeBlock needs "use client".
 */
"use client";

import { CodeBlock } from "@/components/code-block";

interface Props {
  code: string;
  language?: string;
  label?: string;
  showHeader?: boolean;
  className?: string;
}

export function DocsCodeBlock({ code, language, label, showHeader = true, className }: Props) {
  return <CodeBlock code={code} language={language} label={label} showHeader={showHeader} className={className} />;
}

interface SetupCardProps {
  tool: string;
  icon: string;
  iconBg: string;
  configPath: string;
  steps: string[];
  config: string;
}

export function SetupCard({ tool, icon, iconBg, configPath, steps, config }: SetupCardProps) {
  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-[#1e2d44] flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${iconBg}`}>
          {icon}
        </div>
        <div>
          <div className="text-white font-semibold">{tool}</div>
          <div className="text-gray-500 text-xs font-mono">{configPath}</div>
        </div>
      </div>
      <div className="p-6">
        <ol className="list-decimal list-inside text-sm text-gray-400 space-y-2 mb-4">
          {steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <CodeBlock code={config} language="json" />
      </div>
    </div>
  );
}

interface ApiExampleProps {
  title: string;
  method: string;
  endpoint: string;
  body: string;
  response: string;
}

export function ApiExampleCard({ title, method, endpoint, body, response }: ApiExampleProps) {
  return (
    <div className="bg-[#0c1120] border border-[#1e2d44] rounded-xl overflow-hidden">
      <div className="px-5 py-3 border-b border-[#1e2d44] flex items-center gap-3">
        <span className="bg-green-500/15 text-green-400 text-xs font-bold px-2 py-0.5 rounded">
          {method}
        </span>
        <span className="text-white font-mono text-sm">{endpoint}</span>
        <span className="text-gray-500 text-xs ml-auto">{title}</span>
      </div>
      <div className="grid md:grid-cols-2 divide-x divide-[#1e2d44]">
        <div className="p-4">
          <div className="text-gray-500 text-xs mb-2">Request</div>
          <CodeBlock code={body} language="json" showHeader={false} />
        </div>
        <div className="p-4">
          <div className="text-gray-500 text-xs mb-2">Response</div>
          <CodeBlock code={response} language="json" showHeader={false} />
        </div>
      </div>
    </div>
  );
}
