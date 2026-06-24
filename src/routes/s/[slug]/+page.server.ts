import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { db } from '$lib/server/db';

export const load: PageServerLoad = async ({ params }) => {

	const slug = params.slug;

	if (!slug) throw error(400, 'Slug is required');

	const subject = await db.subject.findUnique({
		where: { slug },
		select: { name: true, slug: true, deleted_at: true }
	});
	
	if (!subject || subject.deleted_at) throw error(404, 'Subject not found');
	
	return { subject };
};