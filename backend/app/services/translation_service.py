"""
Translation service — Sarvam AI Mayura for Indian language documentation.

Translates prose documentation into Hindi and other Indian languages.
Code blocks and technical terms are preserved in English.
"""
from __future__ import annotations

import logging
import re

from app.core.config import settings
from app.ingestion.chunker import Chunk
from app.ingestion.embedder import embed_single

logger = logging.getLogger(__name__)

# Technical terms that should NOT be translated
PRESERVE_TERMS = {
    "API", "SDK", "REST", "JSON", "HTTP", "HTTPS", "OAuth", "JWT",
    "webhook", "endpoint", "request", "response", "payload", "token",
    "authentication", "authorization", "GET", "POST", "PUT", "DELETE",
    "npm", "pip", "curl", "bash", "Python", "JavaScript", "TypeScript",
    "Node.js", "React", "Next.js", "FastAPI", "Django",
}


class TranslationService:
    """Translate doc chunks using Sarvam AI Mayura model."""

    LANGUAGE_CODES = {
        "hi": "hi-IN",   # Hindi
        "ta": "ta-IN",   # Tamil
        "te": "te-IN",   # Telugu
        "kn": "kn-IN",   # Kannada
        "bn": "bn-IN",   # Bengali
        "mr": "mr-IN",   # Marathi
        "gu": "gu-IN",   # Gujarati
        "pa": "pa-IN",   # Punjabi
    }

    async def translate_chunks(
        self,
        chunks: list[Chunk],
        target_lang: str,
    ) -> list[Chunk]:
        """Translate a list of chunks to the target language."""
        if not settings.SARVAM_API_KEY:
            logger.warning("SARVAM_API_KEY not set — skipping translation")
            return []

        translated = []
        for chunk in chunks:
            try:
                translated_chunk = await self._translate_chunk(chunk, target_lang)
                if translated_chunk:
                    translated.append(translated_chunk)
            except Exception as e:
                logger.warning(f"Translation failed for chunk {chunk.content_hash}: {e}")

        return translated

    async def _translate_chunk(self, chunk: Chunk, target_lang: str) -> Chunk | None:
        """Translate a single chunk — prose only, preserve code blocks."""
        # Extract and protect code blocks
        code_blocks: dict[str, str] = {}
        prose = _protect_code_blocks(chunk.content, code_blocks)

        # Skip if mostly code
        if len(prose.strip()) < 50:
            return None

        # Translate prose
        translated_prose = await self._call_sarvam_api(prose, target_lang)
        if not translated_prose:
            return None

        # Restore code blocks
        translated_content = _restore_code_blocks(translated_prose, code_blocks)

        # Generate new embedding for translated content
        try:
            new_embedding = await embed_single(translated_content)
        except Exception:
            new_embedding = chunk.embedding  # Fall back to source embedding

        import hashlib
        return Chunk(
            content=translated_content,
            library_id=chunk.library_id,
            url=chunk.url,
            section=chunk.section,
            language=target_lang,
            content_hash=hashlib.sha256(translated_content.encode()).hexdigest(),
            metadata={
                **chunk.metadata,
                "translated_from": "en",
                "translation_model": "sarvam-mayura",
            },
            embedding=new_embedding,
        )

    async def _call_sarvam_api(self, text: str, target_lang: str) -> str | None:
        """Call Sarvam AI Mayura translation API."""
        import httpx

        lang_code = self.LANGUAGE_CODES.get(target_lang, f"{target_lang}-IN")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://api.sarvam.ai/translate",
                    headers={
                        "API-Subscription-Key": settings.SARVAM_API_KEY,
                        "Content-Type": "application/json",
                    },
                    json={
                        "input": text[:2000],  # Sarvam API limit per call
                        "source_language_code": "en-IN",
                        "target_language_code": lang_code,
                        "speaker_gender": "Male",
                        "mode": "formal",
                        "model": "mayura:v1",
                        "enable_preprocessing": True,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("translated_text", "")
                else:
                    logger.warning(f"Sarvam API error {response.status_code}: {response.text[:200]}")
                    return None
        except Exception as e:
            logger.error(f"Sarvam API call failed: {e}")
            return None


def _protect_code_blocks(text: str, code_blocks: dict) -> str:
    def replace(match):
        key = f"__CODE_{len(code_blocks)}__"
        code_blocks[key] = match.group(0)
        return key
    return re.sub(r"```[\s\S]*?```", replace, text)


def _restore_code_blocks(text: str, code_blocks: dict) -> str:
    for key, code in code_blocks.items():
        text = text.replace(key, code)
    return text
