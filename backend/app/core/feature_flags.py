"""
Feature flag system — toggle features on/off via environment variables.

Usage:
    from app.core.feature_flags import flags
    if flags.CODE_SNIPPETS:
        # feature is enabled

All flags default to True in development, configurable via env vars.
Set FEATURE_<NAME>=false to disable a feature.

Runtime overrides (set via the admin API) take precedence over env vars
and persist until the server process restarts.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)

# Runtime overrides set by the admin API.  Maps flag name (e.g. "code_snippets")
# to its boolean override value.  Checked before the environment variable.
_flag_overrides: dict[str, bool] = {}


def _env_bool(key: str, default: bool = True) -> bool:
    """Read a boolean from env. Accepts: true/false/1/0/yes/no."""
    val = os.getenv(key, str(default)).lower().strip()
    return val in ("true", "1", "yes", "on")


class FeatureFlags:
    """Centralized feature flag configuration. All flags are hot-reloadable.

    Runtime overrides (via ``_flag_overrides`` dict) take precedence over
    environment variables.  The admin API writes to ``_flag_overrides``.
    """

    @staticmethod
    def _resolve(override_key: str, env_key: str, default: bool = True) -> bool:
        """Return the override value if set, otherwise fall back to env."""
        if override_key in _flag_overrides:
            return _flag_overrides[override_key]
        return _env_bool(env_key, default)

    # ── P0: Core Features ────────────────────────────────────────
    @property
    def SEARCH(self) -> bool:
        """Hybrid search + reranking (core feature, always on)."""
        return self._resolve("search", "FEATURE_SEARCH", True)

    @property
    def CODE_SNIPPETS(self) -> bool:
        """Generate integration code from documentation context."""
        return self._resolve("code_snippets", "FEATURE_CODE_SNIPPETS", True)

    @property
    def OFFLINE_PACKS(self) -> bool:
        """Downloadable offline documentation bundles."""
        return self._resolve("offline_packs", "FEATURE_OFFLINE_PACKS", True)

    @property
    def HINDI_DOCS(self) -> bool:
        """Hindi + regional language documentation."""
        return self._resolve("hindi_docs", "FEATURE_HINDI_DOCS", True)

    # ── P1: Developer Accelerators ───────────────────────────────
    @property
    def COOKBOOKS(self) -> bool:
        """End-to-end integration cookbooks (multi-API flows)."""
        return self._resolve("cookbooks", "FEATURE_COOKBOOKS", True)

    @property
    def SDK_GENERATION(self) -> bool:
        """Auto-generate SDKs for APIs without official ones."""
        return self._resolve("sdk_generation", "FEATURE_SDK_GENERATION", True)

    @property
    def FRAMEWORK_STARTERS(self) -> bool:
        """Framework-specific starter templates (Next.js+Razorpay, etc.)."""
        return self._resolve("framework_starters", "FEATURE_FRAMEWORK_STARTERS", True)

    @property
    def TEST_GENERATION(self) -> bool:
        """Generate integration test scaffolding from docs."""
        return self._resolve("test_generation", "FEATURE_TEST_GENERATION", True)

    @property
    def OPENAPI_GENERATION(self) -> bool:
        """Generate OpenAPI specs from scraped documentation."""
        return self._resolve("openapi_generation", "FEATURE_OPENAPI_GENERATION", True)

    @property
    def WORKFLOW_TEMPLATES(self) -> bool:
        """Multi-API workflow templates (payments + shipping + notifications)."""
        return self._resolve("workflow_templates", "FEATURE_WORKFLOW_TEMPLATES", True)

    # ── P2: Integrations & Community ─────────────────────────────
    @property
    def JIRA_INTEGRATION(self) -> bool:
        """Jira MCP tool — link docs to tickets."""
        return self._resolve("jira_integration", "FEATURE_JIRA_INTEGRATION", True)

    @property
    def SLACK_NOTIFICATIONS(self) -> bool:
        """Slack webhook notifications on doc changes."""
        return self._resolve("slack_notifications", "FEATURE_SLACK_NOTIFICATIONS", True)

    @property
    def ZOHO_INTEGRATION(self) -> bool:
        """Zoho Projects MCP tool."""
        return self._resolve("zoho_integration", "FEATURE_ZOHO_INTEGRATION", True)

    @property
    def COMPLIANCE_LAYER(self) -> bool:
        """DLT/GSTN/DPDP regulatory guidance overlay."""
        return self._resolve("compliance_layer", "FEATURE_COMPLIANCE_LAYER", True)

    @property
    def ERROR_PATTERNS(self) -> bool:
        """Crowdsourced error patterns + fixes database."""
        return self._resolve("error_patterns", "FEATURE_ERROR_PATTERNS", True)

    @property
    def COMMUNITY_QA(self) -> bool:
        """Community Q&A per API endpoint."""
        return self._resolve("community_qa", "FEATURE_COMMUNITY_QA", True)

    def to_dict(self) -> dict[str, bool]:
        """Return all flags as a dictionary (for API response)."""
        return {
            # P0
            "search": self.SEARCH,
            "code_snippets": self.CODE_SNIPPETS,
            "offline_packs": self.OFFLINE_PACKS,
            "hindi_docs": self.HINDI_DOCS,
            # P1
            "cookbooks": self.COOKBOOKS,
            "sdk_generation": self.SDK_GENERATION,
            "framework_starters": self.FRAMEWORK_STARTERS,
            "test_generation": self.TEST_GENERATION,
            "openapi_generation": self.OPENAPI_GENERATION,
            "workflow_templates": self.WORKFLOW_TEMPLATES,
            # P2
            "jira_integration": self.JIRA_INTEGRATION,
            "slack_notifications": self.SLACK_NOTIFICATIONS,
            "zoho_integration": self.ZOHO_INTEGRATION,
            "compliance_layer": self.COMPLIANCE_LAYER,
            "error_patterns": self.ERROR_PATTERNS,
            "community_qa": self.COMMUNITY_QA,
        }

    def log_status(self) -> None:
        """Log all feature flag states at startup."""
        flags_dict = self.to_dict()
        enabled = [k for k, v in flags_dict.items() if v]
        disabled = [k for k, v in flags_dict.items() if not v]
        logger.info(f"Feature flags: {len(enabled)} enabled, {len(disabled)} disabled")
        if disabled:
            logger.info(f"Disabled features: {', '.join(disabled)}")


# Singleton
flags = FeatureFlags()
