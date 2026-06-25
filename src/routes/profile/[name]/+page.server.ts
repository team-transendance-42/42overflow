import { error, redirect , fail} from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
  if (!locals.user) throw redirect(303, '/login');

  const myProfile = await db.user.findUnique({
    where: { id: locals.user.id }
  });

  const profile = await db.user.findUnique({
    where: { name: params.name},
  });

  if (!profile) throw error(404, 'User not found');

  const isFollowing = myProfile ? await db.follow.findUnique({
    where: {
      followerId_followingId: {
        followerId: myProfile.id,
        followingId: profile.id,
      }
    }
  }) : null;

  const followerCount = await db.follow.count({
    where: { followingId: profile.id }
  });

  const followingCount = await db.follow.count({
    where: { followerId: profile.id }
  });

  const isOnline = profile.last_seen
    ? new Date().getTime() - new Date(profile.last_seen).getTime() < 5 * 60 * 1000
    : false;

  const posts = await db.post.findMany({
	where: { userId: profile.id, deleted_at: null },
	orderBy: { created_at: 'desc' },
	include: {
		subject: true,
		_count: { select: { likes: true, comments: true } }
	}
});

  return {
    profile,
    user: {
      name: profile.name,
      image: profile.image,
    },
    isFollowing: !!isFollowing,
    followerCount,
    followingCount,
    isOnline,
	posts,
    isOwnProfile: myProfile?.id === profile.id,
  };
};

export const actions = {
  follow: async ({ locals, params }) => {
    if (!locals.user) throw redirect(303, '/login');

    const myProfile = await db.user.findUnique({
      where: { id: locals.user.id }
    });

    if (!myProfile) throw error(400, 'Your profile not found');

    const targetProfile = await db.user.findUnique({
      where: { name: params.name }
    });

    if (!targetProfile) throw error(404, 'User not found');

	try {
    const existing = await db.follow.findUnique({
      where: {
        followerId_followingId: {
          followerId: myProfile.id,
          followingId: targetProfile.id,
        }
      }
    });

    if (existing) {
      await db.follow.delete({
        where: {
          followerId_followingId: {
            followerId: myProfile.id,
            followingId: targetProfile.id,
          }
        }
      });
    } else {
      await db.follow.create({
        data: {
          followerId: myProfile.id,
          followingId: targetProfile.id,
        }
      });
    }
}	catch (err) {
		console.error(err);
		return fail(500, { error:'Failed to update follow status' });
	}

    return { success: true };
  }
};