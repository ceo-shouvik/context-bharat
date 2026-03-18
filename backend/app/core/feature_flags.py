"""
Feature flag system — toggle features on/off via environment variables.

Usage:
    from app.core.feature_flags import flags
    if flags.CODE_SNIPPETS:
        # feature is enabled

All flags default to True in development, configurable via env vars.
Set FEATURE_<NAME>=false to disable a feature.
"""
from __future__ import annotations

import os
import logging

logger = logging.getLogger(__name__)


def _env_bool(key: str, default: bool = True) -> bool:
    """Read a boolean from env. Accepts: true/false/1/0/yes/no."""
    val = os.getenv(key, str(default)).lower().strip()
    return val in ("true", "1", "yes", "on")


class FeatureFlags:
    """Centralized feature flag configuration. All flags are hot-reloadable."""

    # ── P0: Core Features ────────────────────────────────────────
    @property
    def SEARCH(self) -> bool:
        """Hybrid search + reranking (core feature, always on)."""
        return _env_bool("FEATURE_SEARCH", True)

    @property
    def CODE_SNIPPETS(self) -> bool:
        """Generate integration code from documentation context."""
        return _env_bool("FEATURE_CODE_SNIPPETS", True)

    @property
    def OFFLINE_PACKS(self) -> bool:
        """Downloadable offline documentation bundles."""
        return _env_bool("FEATURE_OFFLINE_PACKS", True)

    @property
    def HINDI_DOCS(self) -> bool:
        """Hindi + regional language documentation."""
        return _env_bool("FEATURE_HINDI_DOCS", True)

    # ── P1: Developer Accelerators ───────────────────────────────
    @property
    def COOKBOOKS(self) -> bool:
        """End-to-end integration cookbooks (multi-API flows)."""
        return _env_bool("FEATURE_COOKBOOKS", True)

    @property
    def SDK_GENERATION(self) -> bool:
        """Auto-generate SDKs for APIs without official ones."""
        return _env_bool("FEATURE_SDK_GENERATION", True)

    @property
    def FRAMEWORK_STARTERS(self) -> bool:
        """Framework-specific starter templates (Next.js+Razorpay, etc.)."""
        return _env_bool("FEATURE_FRAMEWORK_STARTERS", True)

    @property
    def TEST_GENERATION(self) -> bool:
        """Generate integration test scaffolding from docs."""
        return _env_bool("FEATURE_TEST_GENERATION", True)

    @property
    def OPENAPI_GENERATION(self) -> bool:
        """Generate OpenAPI specs from scraped documentation."""
        return _env_bool("FEATURE_OPENAPI_GENERATION", True)

    @property
    def WORKFLOW_TEMPLATES(self) -> bool:
        """Multi-API workflow templates (payments + shipping + notifications)."""
        return _env_bool("FEATURE_WORKFLOW_TEMPLATES", True)

    # ── P2: Integrations & Community ─────────────────────────────
    @property
    def JIRA_INTEGRATION(self) -> bool:
        """Jira MCP tool — link docs to tickets."""
        return _env_bool("FEATURE_JIRA_INTEGRATION", True)

    @property
    def SLACK_NOTIFICATIONS(self) -> bool:
        """Slack webhook notifications on doc changes."""
        return _env_bool("FEATURE_SLACK_NOTIFICATIONS", True)

    @property
    def ZOHO_INTEGRATION(self) -> bool:
        """Zoho Projects MCP tool."""
        return _env_bool("FEATURE_ZOHO_INTEGRATION", True)

    @property
    def COMPLIANCE_LAYER(self) -> bool:
        """DLT/GSTN/DPDP regulatory guidance overlay."""
        return _env_bool("FEATURE_COMPLIANCE_LAYER", True)

    @property
    def ERROR_PATTERNS(self) -> bool:
        """Crowdsourced error patterns + fixes database."""
        return _env_bool("FEATURE_ERROR_PATTERNS", True)

    @property
    def COMMUNITY_QA(self) -> bool:
        """Community Q&A per API endpoint."""
        return _env_bool("FEATURE_COMMUNITY_QA", True)

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
