import { clients } from '$lib/server/sse';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = ({ request }) => {
	let controller: ReadableStreamDefaultController;

	const stream = new ReadableStream({
		start(c) {
			controller = c;
			clients.add(controller);

			console.log('Client connected:', clients.size);

			const encoder = new TextEncoder();
			controller.enqueue(encoder.encode(': connected\n\n'));
		}
	});

	request.signal.addEventListener('abort', () => {
		if (controller) {
			clients.delete(controller);
			console.log('Client disconnected:', clients.size);
		}
	});

	return new Response(stream, {
		headers: {
			'Content-Type': 'text/event-stream',
			'Cache-Control': 'no-cache',
			Connection: 'keep-alive'
		}
	});
};
