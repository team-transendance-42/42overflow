import { prisma } from '$lib/server/prisma';
import { type SubjectRole } from '@prisma/client';

export async function getSubjectRole(slug: string, userId: string): Promise<SubjectRole | null> {
	const membership = await prisma.subjectMember.findFirst({
		where: {
			userId,
			subject: {
				slug,
				deleted_at: null
			}
		},
		select: {
			role: true
		}
	});

	return membership?.role ?? null;
}