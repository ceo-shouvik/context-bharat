"""SDK generation endpoint — generates basic API client SDKs from documentation."""
from __future__ import annotations

import logging
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.feature_flags import flags

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sdks", tags=["sdk-generation"])


# ─── Schemas ─────────────────────────────────────────────────────────────────

class SDKLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


class GenerateSDKRequest(BaseModel):
    library_id: str = Field(..., description="ContextBharat library ID")
    language: SDKLanguage = Field(default=SDKLanguage.PYTHON)


class GenerateSDKResponse(BaseModel):
    sdk_code: dict[str, str] = Field(
        ..., description="Mapping of filename to file content"
    )
    language: str
    library_name: str


# ─── SDK Templates ───────────────────────────────────────────────────────────

def _get_library_short_name(library_id: str) -> str:
    """Extract short name from library ID."""
    parts = library_id.strip("/").split("/")
    return parts[-1].replace("-", "_") if parts else "api"


def _get_library_class_name(library_id: str) -> str:
    """Generate a PascalCase class name from library ID."""
    short = _get_library_short_name(library_id)
    return "".join(word.capitalize() for word in short.split("_"))


def _generate_python_sdk(library_id: str, lib_name: str, class_name: str) -> dict[str, str]:
    """Generate a Python SDK structure."""
    return {
        "__init__.py": f'''"""Auto-generated SDK for {library_id}."""
from {lib_name}.client import {class_name}Client

__all__ = ["{class_name}Client"]
__version__ = "0.1.0"
''',
        "client.py": f'''"""HTTP client for {library_id} API."""
from __future__ import annotations

import httpx
from typing import Any

from {lib_name}.models import APIResponse, APIError


class {class_name}Client:
    """Client for the {class_name} API.

    Usage:
        client = {class_name}Client(api_key="your_key")
        result = client.get("/endpoint")
    """

    DEFAULT_BASE_URL = "https://api.example.com"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._default_headers(),
        )

    def _default_headers(self) -> dict[str, str]:
        return {{
            "Authorization": f"Bearer {{self.api_key}}",
            "Content-Type": "application/json",
            "User-Agent": "{lib_name}-python/0.1.0",
        }}

    def get(self, path: str, params: dict[str, Any] | None = None) -> APIResponse:
        """Send a GET request."""
        response = self._client.get(path, params=params)
        return self._handle_response(response)

    def post(self, path: str, data: dict[str, Any] | None = None) -> APIResponse:
        """Send a POST request."""
        response = self._client.post(path, json=data)
        return self._handle_response(response)

    def put(self, path: str, data: dict[str, Any] | None = None) -> APIResponse:
        """Send a PUT request."""
        response = self._client.put(path, json=data)
        return self._handle_response(response)

    def delete(self, path: str) -> APIResponse:
        """Send a DELETE request."""
        response = self._client.delete(path)
        return self._handle_response(response)

    def _handle_response(self, response: httpx.Response) -> APIResponse:
        """Parse the HTTP response into an APIResponse or raise APIError."""
        if response.status_code >= 400:
            raise APIError(
                status_code=response.status_code,
                message=response.text,
            )
        return APIResponse(
            status_code=response.status_code,
            data=response.json() if response.content else {{}},
            headers=dict(response.headers),
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "{class_name}Client":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
''',
        "models.py": f'''"""Data models for {library_id} SDK."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class APIResponse:
    """Successful API response."""
    status_code: int
    data: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


class APIError(Exception):
    """API error with status code and message."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {{status_code}}: {{message}}")


@dataclass
class PaginatedResponse:
    """Paginated list response."""
    items: list[dict[str, Any]]
    total: int = 0
    page: int = 1
    per_page: int = 20
    has_more: bool = False
''',
        "py.typed": "",
    }


def _generate_javascript_sdk(library_id: str, lib_name: str, class_name: str) -> dict[str, str]:
    """Generate a JavaScript SDK structure."""
    return {
        "index.js": f'''/**
 * Auto-generated SDK for {library_id}
 * @module {lib_name}
 */
const {{ {class_name}Client }} = require("./client");

module.exports = {{ {class_name}Client }};
''',
        "client.js": f'''/**
 * HTTP client for {library_id} API.
 */
class {class_name}Client {{
  /**
   * @param {{{{ apiKey: string, baseUrl?: string, timeout?: number }}}} options
   */
  constructor({{ apiKey, baseUrl = "https://api.example.com", timeout = 30000 }}) {{
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\\/$/, "");
    this.timeout = timeout;
  }}

  /**
   * Send a GET request.
   * @param {{string}} path - API endpoint path
   * @param {{Object}} [params] - Query parameters
   * @returns {{Promise<Object>}}
   */
  async get(path, params = {{}}) {{
    const url = new URL(`${{this.baseUrl}}${{path}}`);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    return this._request(url.toString(), {{ method: "GET" }});
  }}

  /**
   * Send a POST request.
   * @param {{string}} path - API endpoint path
   * @param {{Object}} [data] - Request body
   * @returns {{Promise<Object>}}
   */
  async post(path, data = {{}}) {{
    return this._request(`${{this.baseUrl}}${{path}}`, {{
      method: "POST",
      body: JSON.stringify(data),
    }});
  }}

  /**
   * Send a PUT request.
   * @param {{string}} path - API endpoint path
   * @param {{Object}} [data] - Request body
   * @returns {{Promise<Object>}}
   */
  async put(path, data = {{}}) {{
    return this._request(`${{this.baseUrl}}${{path}}`, {{
      method: "PUT",
      body: JSON.stringify(data),
    }});
  }}

  /**
   * Send a DELETE request.
   * @param {{string}} path - API endpoint path
   * @returns {{Promise<Object>}}
   */
  async delete(path) {{
    return this._request(`${{this.baseUrl}}${{path}}`, {{ method: "DELETE" }});
  }}

  async _request(url, options) {{
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {{
      const response = await fetch(url, {{
        ...options,
        signal: controller.signal,
        headers: {{
          Authorization: `Bearer ${{this.apiKey}}`,
          "Content-Type": "application/json",
          "User-Agent": "{lib_name}-js/0.1.0",
        }},
      }});

      if (!response.ok) {{
        const text = await response.text();
        throw new Error(`API Error ${{response.status}}: ${{text}}`);
      }}

      const data = response.headers.get("content-length") !== "0"
        ? await response.json()
        : {{}};

      return {{ statusCode: response.status, data, headers: Object.fromEntries(response.headers) }};
    }} finally {{
      clearTimeout(timer);
    }}
  }}
}}

module.exports = {{ {class_name}Client }};
''',
        "package.json": f'''{{
  "name": "{lib_name}",
  "version": "0.1.0",
  "description": "Auto-generated SDK for {library_id}",
  "main": "index.js",
  "keywords": ["{lib_name}", "api", "sdk"],
  "license": "MIT"
}}
''',
    }


def _generate_typescript_sdk(library_id: str, lib_name: str, class_name: str) -> dict[str, str]:
    """Generate a TypeScript SDK structure."""
    return {
        "index.ts": f'''/**
 * Auto-generated SDK for {library_id}
 */
export {{ {class_name}Client }} from "./client";
export type {{ APIResponse, APIError, ClientOptions }} from "./types";
''',
        "client.ts": f'''/**
 * HTTP client for {library_id} API.
 */
import type {{ APIResponse, APIError, ClientOptions }} from "./types";

export class {class_name}Client {{
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(options: ClientOptions) {{
    this.apiKey = options.apiKey;
    this.baseUrl = (options.baseUrl ?? "https://api.example.com").replace(/\\/$/, "");
    this.timeout = options.timeout ?? 30000;
  }}

  async get<T = Record<string, unknown>>(
    path: string,
    params?: Record<string, string>,
  ): Promise<APIResponse<T>> {{
    const url = new URL(`${{this.baseUrl}}${{path}}`);
    if (params) {{
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    }}
    return this.request<T>(url.toString(), {{ method: "GET" }});
  }}

  async post<T = Record<string, unknown>>(
    path: string,
    data?: Record<string, unknown>,
  ): Promise<APIResponse<T>> {{
    return this.request<T>(`${{this.baseUrl}}${{path}}`, {{
      method: "POST",
      body: JSON.stringify(data ?? {{}}),
    }});
  }}

  async put<T = Record<string, unknown>>(
    path: string,
    data?: Record<string, unknown>,
  ): Promise<APIResponse<T>> {{
    return this.request<T>(`${{this.baseUrl}}${{path}}`, {{
      method: "PUT",
      body: JSON.stringify(data ?? {{}}),
    }});
  }}

  async delete<T = Record<string, unknown>>(path: string): Promise<APIResponse<T>> {{
    return this.request<T>(`${{this.baseUrl}}${{path}}`, {{ method: "DELETE" }});
  }}

  private async request<T>(url: string, options: RequestInit): Promise<APIResponse<T>> {{
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);

    try {{
      const response = await fetch(url, {{
        ...options,
        signal: controller.signal,
        headers: {{
          Authorization: `Bearer ${{this.apiKey}}`,
          "Content-Type": "application/json",
          "User-Agent": "{lib_name}-ts/0.1.0",
        }},
      }});

      if (!response.ok) {{
        const text = await response.text();
        const error: APIError = {{
          statusCode: response.status,
          message: text,
        }};
        throw error;
      }}

      const data: T = response.headers.get("content-length") !== "0"
        ? await response.json()
        : ({{}} as T);

      return {{ statusCode: response.status, data }};
    }} finally {{
      clearTimeout(timer);
    }}
  }}
}}
''',
        "types.ts": f'''/**
 * Type definitions for {library_id} SDK.
 */

export interface ClientOptions {{
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
}}

export interface APIResponse<T = Record<string, unknown>> {{
  statusCode: number;
  data: T;
}}

export interface APIError {{
  statusCode: number;
  message: string;
}}

export interface PaginatedResponse<T = Record<string, unknown>> {{
  items: T[];
  total: number;
  page: number;
  perPage: number;
  hasMore: boolean;
}}
''',
        "tsconfig.json": f'''{{
  "compilerOptions": {{
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }},
  "include": ["*.ts"]
}}
''',
        "package.json": f'''{{
  "name": "{lib_name}",
  "version": "0.1.0",
  "description": "Auto-generated TypeScript SDK for {library_id}",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {{
    "build": "tsc",
    "prepublishOnly": "npm run build"
  }},
  "keywords": ["{lib_name}", "api", "sdk", "typescript"],
  "license": "MIT"
}}
''',
    }


SDK_GENERATORS = {
    "python": _generate_python_sdk,
    "javascript": _generate_javascript_sdk,
    "typescript": _generate_typescript_sdk,
}


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/generate", response_model=GenerateSDKResponse)
async def generate_sdk(request: GenerateSDKRequest) -> GenerateSDKResponse:
    """
    Generate a basic API client SDK for a library.

    Produces a complete, installable SDK package with HTTP client, models,
    error handling, and type definitions. The generated SDK follows best
    practices for the target language.
    """
    if not flags.SDK_GENERATION:
        raise HTTPException(status_code=404, detail="Feature not enabled")

    lib_name = _get_library_short_name(request.library_id)
    class_name = _get_library_class_name(request.library_id)
    language = request.language.value

    generator = SDK_GENERATORS.get(language)
    if generator is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language}. Supported: {list(SDK_GENERATORS.keys())}",
        )

    try:
        sdk_code = generator(request.library_id, lib_name, class_name)
        return GenerateSDKResponse(
            sdk_code=sdk_code,
            language=language,
            library_name=lib_name,
        )
    except Exception as e:
        logger.error(
            "SDK generation failed",
            extra={"library_id": request.library_id, "language": language},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"SDK generation failed: {e}")
