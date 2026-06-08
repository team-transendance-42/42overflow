import type { RequestHandler } from '@sveltejs/kit';
import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import { SubjectRole } from '@prisma/client';

export const POST: RequestHandler = async ({ params, locals }) => {
  const { slug } = params;

  if (!locals.user) throw error(401, 'Unauthorized');
  if (!slug) throw error(400, 'Slug is required');

  const subject = await db.subject.findUnique({
    where: { slug },
    select: { id: true, deleted_at: true }
  });

  if (!subject || subject.deleted_at) throw error(404, 'Subject not found');

  const membership = await db.subjectMember.upsert({
    where: {
      userId_subjectId: {
        userId: locals.user.id,
        subjectId: subject.id
      }
    },
    update: {}, // already subscribed
    create: {
      userId: locals.user.id,
      subjectId: subject.id,
      role: SubjectRole.MEMBER
    }
  });

  return json(membership, { status: 201 });
};

export const DELETE: RequestHandler = async ({ params, locals }) => {
  const { slug } = params;

  if (!locals.user) throw error(401, 'Unauthorized');
  if (!slug) throw error(400, 'Slug is required');

  const subject = await db.subject.findUnique({
    where: { slug },
    select: { id: true, deleted_at: true }
  });

  if (!subject || subject.deleted_at) throw error(404, 'Subject not found');
  const membership = await db.subjectMember.findUnique({
    where: {
      userId_subjectId: {
        userId: locals.user.id,
        subjectId: subject.id
      }
    },
    select: { role: true }
  });

  if (!membership) throw error(404, 'Subscription not found');

  if (membership.role === SubjectRole.OWNER) {
    const ownerCount = await db.subjectMember.count({
      where: { subjectId: subject.id, role: SubjectRole.OWNER }
    });

    if (ownerCount <= 1) {
      throw error(400, 'Cannot unsubscribe: subject must have at least one owner');
    }
  }

  await db.subjectMember.delete({
    where: {
      userId_subjectId: {
        userId: locals.user.id,
        subjectId: subject.id
      }
    }
  });

  return json({ ok: true }, { status: 200 }); 
};
