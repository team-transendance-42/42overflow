// Auth-gated proxy to the Whisper STT service.
// Parses and re-creates the FormData rather than streaming request.body directly —
// Node.js undici can fail intermittently when forwarding an incoming ReadableStream
// as a multipart body, which caused the 502s after the HTTPS/SvelteKit proxy was introduced.
import type { RequestHandler } from '@sveltejs/kit';
import { error } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) throw error(401, 'Unauthorized');
    if (!env.LLM_INTERNAL_SECRET) throw error(500, 'LLM_INTERNAL_SECRET is not configured');

    let form: FormData;
    try {
        form = await request.formData();
    } catch {
        throw error(400, 'Invalid multipart form data');
    }

    let res: Response;
    try {
        // Do NOT set Content-Type manually — letting fetch set it ensures the
        // multipart boundary in the header matches the actual body boundary.
        res = await fetch('http://python-stt:8091/convert_audio', {
            method: 'POST',
            headers: {
                'X-Internal-Secret': env.LLM_INTERNAL_SECRET,
                'X-User-ID': locals.user.id,
            },
            body: form,
        });
    } catch {
        throw error(502, 'STT service unreachable');
    }

    return new Response(res.body, {
        status: res.status,
        headers: { 'Content-Type': res.headers.get('Content-Type') ?? 'application/json' },
    });
};
