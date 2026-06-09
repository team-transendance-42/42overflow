import { error } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export async function proxyLLM(
    targetUrl: string,
    request: Request,
    user: { id: string } | null,
    options: { streaming?: boolean } = {}
): Promise<Response> {
    if (!user) throw error(401, 'Unauthorized');
    if (!env.LLM_INTERNAL_SECRET) throw error(500, 'LLM_INTERNAL_SECRET is not configured');

    let res: Response;
    try {
        res = await fetch(targetUrl, {
            method: 'POST',
            headers: {
                'Content-Type': request.headers.get('Content-Type') ?? 'application/json',
                'X-Internal-Secret': env.LLM_INTERNAL_SECRET,
                'X-User-ID': user.id,
            },
            body: request.body,
            signal: request.signal,
            // @ts-expect-error — Node fetch requires this when streaming the request body
            duplex: 'half',
        });
    } catch {
        throw error(502, 'LLM service unreachable');
    }

    const responseHeaders: Record<string, string> = {
        'Content-Type': res.headers.get('Content-Type') ?? 'application/octet-stream',
    };

    if (options.streaming) {
        responseHeaders['Cache-Control'] = 'no-cache';
        responseHeaders['X-Accel-Buffering'] = 'no';
    }

    return new Response(res.body, {
        status: res.status,
        headers: responseHeaders,
    });
}
