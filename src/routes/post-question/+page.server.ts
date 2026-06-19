import { json } from "@sveltejs/kit";
import { db } from '$lib/server/db';
import type { PageServerLoad } from './$types.js';

export const load: PageServerLoad = async ({ }) => {
	try {
		const subjectList = await db.subject.findMany({
			where: { deleted_at: null },
			orderBy: { name: 'asc' },
			select: {
				id: true,
				name: true
			}
		})
		return ({ subjectList });
	} catch (err) {
		console.error('Error fetching subjects:', err);
		return (json({ error: 'Failed to fetch subjects' }, { status: 500 }));
	}
};