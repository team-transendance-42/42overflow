import { db } from '$lib/server/db';

type CreateNotificationInput = {
	userId: string;
	content: string;
	link: string;
};

export async function createNotification({ userId, content, link }: CreateNotificationInput) {
	try {
		return db.notification.create({
			data: {
				userId,
				content,
				link,
			}
		});
	} catch (error) {
		console.error('Error creating notification:', error);
		throw new Error('Failed to create notification');
	}
}