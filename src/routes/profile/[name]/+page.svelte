<script lang="ts">
	import Avatar from '$lib/components/Avatar.svelte';
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';

	export let data;

	$: ({ profile, user, isFollowing, followerCount, followingCount, isOnline, isOwnProfile, posts } = data);
</script>

<div class="profile-page">
	<div class="avatar-row">
		<div class="avatar-wrap">
			<Avatar src={user?.image ?? ''}/>
			<span class="status-dot {isOnline ? 'online' : 'offline'}"></span>
		</div>

		<div class="info">
			<h1>{user?.name ?? 'No name set'}</h1>
			<p class="online-text">{isOnline ? 'Online' : 'Offline'}</p>
			<div class="counts">
				<span><strong>{followerCount}</strong> followers</span>
				<span><strong>{followingCount}</strong> following</span>
			</div>
		</div>
	</div>

	<!-- Follow/Unfollow Button -->
	<div class="mb-2">
		{#if !isOwnProfile}
			<form
				method="POST"
				action="?/follow"
				use:enhance={() => {
					return async ({ update }) => {
						await update();
						await invalidateAll();
					};
				}}
			>
				<button
					type="submit"
					class="button small {isFollowing ? 'primary' : 'confirm'}"
				>
					{isFollowing ? 'Unfollow' : 'Follow'}
				</button>
			</form>
		<!-- Edit Button -->
		{:else}
			<a href="/edit-profile" class="button small">Edit profile</a>
		{/if}
	</div>

	{#if profile?.interests}
		<div class="section">
			<span class="label">Interests</span>
			<p>{profile.interests}</p>
		</div>
	{/if}

	{#if posts?.length}
		<div class="section">
			<span class="label">Posts</span>
			{#each posts as post}
				<a href="/posts/{post.id}" class="profile-postbox">
					<h1 class="break-all line-clamp-1"><strong>{post.title}</strong></h1>
					<p class="post-content break-all line-clamp-1">{post.content}</p>
				</a>
			{/each}
		</div>
	{:else}
		<div class="section">
			<span class="label">Posts</span>
			<p class="no-posts">No posts yet.</p>
		</div>
	{/if}
</div>
