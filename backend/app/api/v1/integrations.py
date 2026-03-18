"""Jira, Slack, and Zoho integration endpoints."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])


# ── Pydantic Models ──────────────────────────────────────────────


class JiraLinkRequest(BaseModel):
    """Request to link a library doc to a Jira ticket."""

    library_id: str = Field(
        ..., description="Canonical library ID, e.g. /razorpay/razorpay-sdk"
    )
    jira_url: HttpUrl = Field(
        ..., description="Jira instance URL, e.g. https://myteam.atlassian.net"
    )
    ticket_key: str = Field(
        ..., description="Jira ticket key, e.g. PAY-123", pattern=r"^[A-Z]+-\d+$"
    )
    summary: str = Field(
        ..., description="Brief summary of the link context", max_length=500
    )


class JiraLinkResponse(BaseModel):
    """Response after linking a library doc to a Jira ticket."""

    linked: bool
    ticket_key: str
    library_id: str
    linked_at: str


class SlackNotifyRequest(BaseModel):
    """Request to send a doc update notification to Slack."""

    library_id: str = Field(
        ..., description="Canonical library ID, e.g. /razorpay/razorpay-sdk"
    )
    channel_webhook_url: HttpUrl = Field(
        ..., description="Slack incoming webhook URL"
    )
    message: str = Field(
        ...,
        description="Notification message to send",
        min_length=1,
        max_length=3000,
    )


class SlackNotifyResponse(BaseModel):
    """Response after sending a Slack notification."""

    sent: bool
    library_id: str
    sent_at: str


class ZohoLinkRequest(BaseModel):
    """Request to link a library doc to a Zoho Projects task."""

    library_id: str = Field(
        ..., description="Canonical library ID, e.g. /razorpay/razorpay-sdk"
    )
    project_id: str = Field(..., description="Zoho Projects project ID")
    task_id: str = Field(..., description="Zoho Projects task ID")


class ZohoLinkResponse(BaseModel):
    """Response after linking a library doc to a Zoho Projects task."""

    linked: bool
    library_id: str
    project_id: str
    task_id: str
    linked_at: str


class IntegrationStatusItem(BaseModel):
    """Status of a single integration."""

    name: str
    enabled: bool
    description: str


class IntegrationStatusResponse(BaseModel):
    """Response with the status of all configured integrations."""

    integrations: list[IntegrationStatusItem]


# ── In-Memory Store (MVP) ────────────────────────────────────────

_jira_links: list[dict] = []
_zoho_links: list[dict] = []


# ── Endpoints ────────────────────────────────────────────────────


@router.post("/jira/link", response_model=JiraLinkResponse)
async def link_jira_ticket(request: JiraLinkRequest) -> JiraLinkResponse:
    """
    Link a library doc to a Jira ticket.

    Stores the association so developers can trace documentation references
    back to their project management tickets. Useful for audit trails and
    onboarding: "which docs did we reference when building feature X?"
    """
    if not flags.JIRA_INTEGRATION:
        raise HTTPException(
            status_code=403,
            detail="Jira integration is disabled. Set FEATURE_JIRA_INTEGRATION=true to enable.",
        )

    now = datetime.now(timezone.utc).isoformat()
    link_record = {
        "library_id": request.library_id,
        "jira_url": str(request.jira_url),
        "ticket_key": request.ticket_key,
        "summary": request.summary,
        "linked_at": now,
    }
    _jira_links.append(link_record)
    logger.info(
        "Linked library to Jira ticket",
        extra={"library_id": request.library_id, "ticket_key": request.ticket_key},
    )

    return JiraLinkResponse(
        linked=True,
        ticket_key=request.ticket_key,
        library_id=request.library_id,
        linked_at=now,
    )


@router.post("/slack/notify", response_model=SlackNotifyResponse)
async def slack_notify(request: SlackNotifyRequest) -> SlackNotifyResponse:
    """
    Send a doc update notification to a Slack channel via incoming webhook.

    For MVP, this validates the request and records intent. In production,
    this would POST to the Slack webhook URL with the formatted message.
    """
    if not flags.SLACK_NOTIFICATIONS:
        raise HTTPException(
            status_code=403,
            detail="Slack notifications are disabled. Set FEATURE_SLACK_NOTIFICATIONS=true to enable.",
        )

    now = datetime.now(timezone.utc).isoformat()

    # MVP: log the notification intent. Production would use httpx.AsyncClient
    # to POST to the webhook URL with the Slack Block Kit payload.
    logger.info(
        "Slack notification queued",
        extra={
            "library_id": request.library_id,
            "webhook_url": str(request.channel_webhook_url)[:40] + "...",
            "message_length": len(request.message),
        },
    )

    return SlackNotifyResponse(
        sent=True,
        library_id=request.library_id,
        sent_at=now,
    )


@router.post("/zoho/link", response_model=ZohoLinkResponse)
async def link_zoho_task(request: ZohoLinkRequest) -> ZohoLinkResponse:
    """
    Link a library doc to a Zoho Projects task.

    Stores the association between a Context Bharat library and a Zoho
    Projects task for traceability.
    """
    if not flags.ZOHO_INTEGRATION:
        raise HTTPException(
            status_code=403,
            detail="Zoho integration is disabled. Set FEATURE_ZOHO_INTEGRATION=true to enable.",
        )

    now = datetime.now(timezone.utc).isoformat()
    link_record = {
        "library_id": request.library_id,
        "project_id": request.project_id,
        "task_id": request.task_id,
        "linked_at": now,
    }
    _zoho_links.append(link_record)
    logger.info(
        "Linked library to Zoho task",
        extra={
            "library_id": request.library_id,
            "project_id": request.project_id,
            "task_id": request.task_id,
        },
    )

    return ZohoLinkResponse(
        linked=True,
        library_id=request.library_id,
        project_id=request.project_id,
        task_id=request.task_id,
        linked_at=now,
    )


@router.get("/status", response_model=IntegrationStatusResponse)
async def integration_status() -> IntegrationStatusResponse:
    """
    Show which integrations are currently configured and enabled.

    Each integration's status is determined by its feature flag.
    """
    return IntegrationStatusResponse(
        integrations=[
            IntegrationStatusItem(
                name="jira",
                enabled=flags.JIRA_INTEGRATION,
                description="Link library docs to Jira tickets for project traceability.",
            ),
            IntegrationStatusItem(
                name="slack",
                enabled=flags.SLACK_NOTIFICATIONS,
                description="Send doc update notifications to Slack channels via webhook.",
            ),
            IntegrationStatusItem(
                name="zoho",
                enabled=flags.ZOHO_INTEGRATION,
                description="Link library docs to Zoho Projects tasks.",
            ),
        ]
    )
