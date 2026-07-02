import type { RequestHandler } from '@sveltejs/kit';
import { proxyLLM } from '$lib/server/llmProxy';
import { error } from '@sveltejs/kit';

const PROVIDER_URLS: Record<string, string> = {
    community: 'http://llm-server:8081/api/ai/community',
    gemini:    'http://llm-server:8081/api/ai/gemini',
    ollama:    'http://llm-server:8081/api/ai/ollama',
};

export const POST: RequestHandler = ({ params, request, locals }) => {
    const url = PROVIDER_URLS[params.provider];
    if (!url) throw error(404, 'Unknown provider');
    return proxyLLM(url, request, locals.user, { streaming: true });
};
