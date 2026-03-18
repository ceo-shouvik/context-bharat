/**
 * Feature flags for the frontend.
 * Toggle features via environment variables: NEXT_PUBLIC_FEATURE_<NAME>=false
 * All default to true in development.
 */

function envBool(key: string, defaultVal: boolean = true): boolean {
  const val = process.env[key]?.toLowerCase().trim();
  if (val === undefined) return defaultVal;
  return val === "true" || val === "1" || val === "yes";
}

export const features = {
  // P0: Core
  search: envBool("NEXT_PUBLIC_FEATURE_SEARCH"),
  codeSnippets: envBool("NEXT_PUBLIC_FEATURE_CODE_SNIPPETS"),
  offlinePacks: envBool("NEXT_PUBLIC_FEATURE_OFFLINE_PACKS"),
  hindiDocs: envBool("NEXT_PUBLIC_FEATURE_HINDI_DOCS"),

  // P1: Developer Accelerators
  cookbooks: envBool("NEXT_PUBLIC_FEATURE_COOKBOOKS"),
  sdkGeneration: envBool("NEXT_PUBLIC_FEATURE_SDK_GENERATION"),
  frameworkStarters: envBool("NEXT_PUBLIC_FEATURE_FRAMEWORK_STARTERS"),
  testGeneration: envBool("NEXT_PUBLIC_FEATURE_TEST_GENERATION"),
  openapiGeneration: envBool("NEXT_PUBLIC_FEATURE_OPENAPI_GENERATION"),
  workflowTemplates: envBool("NEXT_PUBLIC_FEATURE_WORKFLOW_TEMPLATES"),

  // P2: Integrations & Community
  jiraIntegration: envBool("NEXT_PUBLIC_FEATURE_JIRA_INTEGRATION"),
  slackNotifications: envBool("NEXT_PUBLIC_FEATURE_SLACK_NOTIFICATIONS"),
  zohoIntegration: envBool("NEXT_PUBLIC_FEATURE_ZOHO_INTEGRATION"),
  complianceLayer: envBool("NEXT_PUBLIC_FEATURE_COMPLIANCE_LAYER"),
  errorPatterns: envBool("NEXT_PUBLIC_FEATURE_ERROR_PATTERNS"),
  communityQa: envBool("NEXT_PUBLIC_FEATURE_COMMUNITY_QA"),
} as const;

export type FeatureKey = keyof typeof features;
