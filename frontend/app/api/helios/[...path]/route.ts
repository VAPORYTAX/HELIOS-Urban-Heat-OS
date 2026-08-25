import { NextRequest, NextResponse } from "next/server";

const HELIOS_BACKEND = process.env.HELIOS_BACKEND_URL ?? "http://127.0.0.1:8080/api/v1";

async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const { path } = await context.params;

  const target = new URL(
    `${HELIOS_BACKEND}/${path.map(encodeURIComponent).join("/")}`
  );

  request.nextUrl.searchParams.forEach((value, key) => {
    target.searchParams.append(key, value);
  });

  const init: RequestInit = {
    method: request.method,
    headers: {
      "Content-Type": request.headers.get("content-type") ?? "application/json",
      "Accept": request.headers.get("accept") ?? "application/json",
    },
    cache: "no-store",
  };

  if (!["GET", "HEAD"].includes(request.method)) {
    init.body = await request.text();
  }

  try {
    const response = await fetch(target, init);
    const body = await response.arrayBuffer();

    return new NextResponse(body, {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get("content-type") ?? "application/json",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: "HELIOS backend unavailable",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 502 }
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;

