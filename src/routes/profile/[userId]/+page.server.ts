import { error, redirect } from '@sveltejs/kit';
import { db } from '$lib/server/db';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
  if (!locals.user) throw redirect(303, '/login');

  // get the logged-in user's profile
  const myProfile = await db.profile.findUnique({
    where: { userId: locals.user.id }
  });

  const profile = await db.profile.findUnique({
    where: { userId: params.userId },
    include: { user: true }
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

  const isOnline = profile.lastSeen
    ? new Date().getTime() - new Date(profile.lastSeen).getTime() < 5 * 60 * 1000
    : false;

  return {
    profile,
    user: {
      name: profile.user.name,
      image: profile.user.image,
    },
    isFollowing: !!isFollowing,
    followerCount,
    followingCount,
    isOnline,
    isOwnProfile: locals.user.id === params.userId,
  };
};  


export const actions = {
  follow: async ({ locals, params }) => {
    if (!locals.user) throw redirect(303, '/login');

    // get both profiles
    const myProfile = await db.profile.findUnique({
      where: { userId: locals.user.id }
    });

    if (!myProfile) throw error(400, 'Your profile not found');

    const targetProfile = await db.profile.findUnique({
      where: { userId: params.userId }
    });

    if (!targetProfile) throw error(404, 'User not found');

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

    return { success: true };
  }
};