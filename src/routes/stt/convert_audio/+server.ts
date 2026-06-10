// Auth-gated proxy to the Whisper STT service. proxyLLM returns 401 if not logged in.
// Accepts multipart/form-data with a 'file' field (audio blob) — same format as before.
import type { RequestHandler } from '@sveltejs/kit';
import { proxyLLM } from '$lib/server/llmProxy';

export const POST: RequestHandler = ({ request, locals }) =>
    proxyLLM('http://python-stt:8091/convert_audio', request, locals.user);
