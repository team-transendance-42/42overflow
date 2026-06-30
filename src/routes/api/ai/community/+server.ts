import type { RequestHandler } from '@sveltejs/kit';
import { proxyLLM } from '$lib/server/llmProxy';

export const POST: RequestHandler = ({ request, locals }) =>
    proxyLLM('http://llm-server:8081/api/ai/community', request, locals.user, { streaming: true });
