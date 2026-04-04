/**
 * API proxy — forwards requests to the backend API.
 * Avoids CORS issues by keeping all fetches same-origin.
 */
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://contextbharat-api-507218003648.asia-south1.run.app";

export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const backendPath = `/v1/${path.join("/")}`;
  const url = new URL(backendPath, BACKEND_URL);
  url.search = request.nextUrl.search;

  const response = await fetch(url.toString(), {
    headers: {
      "Content-Type": "application/json",
      ...(request.headers.get("authorization")
        ? { Authorization: request.headers.get("authorization")! }
        : {}),
    },
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const backendPath = `/v1/${path.join("/")}`;
  const url = new URL(backendPath, BACKEND_URL);

  const body = await request.json();
  const response = await fetch(url.toString(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(request.headers.get("authorization")
        ? { Authorization: request.headers.get("authorization")! }
        : {}),
    },
    body: JSON.stringify(body),
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
}
