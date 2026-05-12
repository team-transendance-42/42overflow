import { json, error } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ url }) => {
  const page = Number(url.searchParams.get('page')) || 1;
  const limit = Number(url.searchParams.get('limit')) || 5;

  const [posts, total] = await Promise.all([
	db.post.findMany({
	  skip: (page - 1) * limit,
	  take: limit,
	  orderBy: { created_at: 'desc' },
	  where: { deleted_at: null },
	  include: {
		user: { select: { name: true } }
	  }
	}),
	db.post.count({ where: { deleted_at: null } })
  ]);

  return json({ data: posts, total });
};

export const POST: RequestHandler = async ({ request, locals }) => {
  if (!locals.user) throw error(401, 'Unauthorized');

  const myProfile = await db.user.findUnique({
	where: { id: locals.user.id }
  });

  if (!myProfile) throw error(400, 'Profile not found');

const { projectname, topic, body } = await request.json();

const post = await db.post.create({
  data: {
	title: projectname,
	content: `${topic}\n\n${body}`,
	userId: myProfile.id
  }
});

  return json(post, { status: 201 });
};
