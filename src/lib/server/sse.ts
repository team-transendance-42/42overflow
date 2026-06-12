export const clients = new Set<ReadableStreamDefaultController>();

type SSEEvent =
	| { type: 'comment-create'; comment: any }
	| { type: 'comment-update'; comment: any }
	| { type: 'comment-delete'; commentId: number }
	| { type: 'like-update'; commentId: number; likeCount: number; userLiked: boolean };

export function broadcast(event: SSEEvent) {
	const msg = `data: ${JSON.stringify(event)}\n\n`;

	for (const client of [...clients]) {
		try {
			client.enqueue(msg);
		} catch {
			clients.delete(client);
		}
	}
}
