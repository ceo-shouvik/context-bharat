/**
 * Cloudflare Worker: Proxy custom subdomains to Google Cloud Run
 *
 * Cloud Run returns 404 for requests with custom Host headers it doesn't recognize.
 * This worker rewrites the Host header to the Cloud Run service URL so the request
 * is routed correctly, while preserving everything else (method, body, headers).
 */

const ORIGIN_MAP: Record<string, string> = {
	"api.contextbharat.com": "contextbharat-api-507218003648.asia-south1.run.app",
	"mcp.contextbharat.com": "contextbharat-mcp-507218003648.asia-south1.run.app",
};

const CORS_HEADERS: Record<string, string> = {
	"Access-Control-Allow-Origin": "*",
	"Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
	"Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
	"Access-Control-Max-Age": "86400",
};

export default {
	async fetch(request: Request): Promise<Response> {
		const url = new URL(request.url);
		const hostname = url.hostname;

		// Handle CORS preflight
		if (request.method === "OPTIONS") {
			return new Response(null, {
				status: 204,
				headers: CORS_HEADERS,
			});
		}

		const origin = ORIGIN_MAP[hostname];
		if (!origin) {
			return new Response("Unknown host", { status: 421 });
		}

		// Build the proxied URL, replacing hostname with Cloud Run origin
		const proxyUrl = new URL(url.toString());
		proxyUrl.hostname = origin;
		proxyUrl.port = "443";
		proxyUrl.protocol = "https:";

		// Clone headers, rewrite Host to Cloud Run's expected hostname
		const headers = new Headers(request.headers);
		headers.set("Host", origin);
		headers.set("X-Forwarded-Host", hostname);

		const response = await fetch(proxyUrl.toString(), {
			method: request.method,
			headers,
			body: request.body,
			redirect: "follow",
		});

		// Clone response and append CORS headers
		const responseHeaders = new Headers(response.headers);
		for (const [key, value] of Object.entries(CORS_HEADERS)) {
			responseHeaders.set(key, value);
		}

		return new Response(response.body, {
			status: response.status,
			statusText: response.statusText,
			headers: responseHeaders,
		});
	},
} satisfies ExportedHandler;
