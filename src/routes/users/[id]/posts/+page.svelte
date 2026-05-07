<script lang="ts">

	type UserRole = 'USER' | 'MODERATOR' | 'ADMIN';

	type UserDetails = {
		id: string;
		name: string;
		first_name: string | null;
		last_name: string | null;
		email: string;
		image: string | null;
		role: UserRole;
		createdAt: string | Date;
		updatedAt: string | Date;
		biography: string | null;
		interests: string | null;
	};

	type UserPost = {
		id: number;
		title: string;
		content: string;
		created_at: string | Date;
		deleted_at: string | Date | null;
	};

	type FormState = {
		success?: boolean;
		message?: string;
	};

	let {
		data,
		form
	}: {
		data: {
			user: UserDetails;
			posts: UserPost[];
		};
		form: FormState | null;
	} = $props();

	function formatDate(value: string | Date) {
		return new Date(value).toLocaleDateString();
	}

	function confirmDelete(event: SubmitEvent) {
		const ok = window.confirm('Are you sure you want to delete this user? This action cannot be undone.');
		if (!ok) {
			// Prevent form submission
			event.preventDefault();
		}
	}
</script>

<div class="edit-user-page">
	<a href="/users" class="back-link">Back to users</a>
		<nav class="tabs">
 			 <a
				href={`/users/${data.user.id}`}
				class="tab"
				class:active={false}
				>Profile</a
			>
			<a href={`/users/${data.user.id}/posts`} class="tab" class:active={true}>Posts</a>
			<a href={`/users/${data.user.id}/comments`} class="tab" class:active={false}>Comments</a>
		</nav>

		{#if data.posts.length === 0}
			<p>This user has no posts.</p>
		{:else}
			{#each data.posts as post}
				<section class="card">
					<p>{post.title}</p>
					<p>{post.content}</p>
					<div class="post-actions">
						<form method="POST" action="?/deletePost" onsubmit={confirmDelete}>
							<input type="hidden" name="postId" value={post.id} />
							<button type="submit" style="background-color: red;">Delete Post</button>
						</form>
						<a href={`/posts/${post.id}`} style="color: blue;">View Post</a>
					</div>					
				</section>
			{/each}
		{/if}
</div>

<style>
	.tabs {
		display: flex;
		gap: 0.5rem;
		border-bottom: 1px solid var(--color-neutral-300);
		margin-bottom: 1rem;
  	}

  	.tab {
		padding: 0.5rem 0.9rem;
		text-decoration: none;
		color: var(--color-text-primary);
		background: transparent;
		border: 1px solid transparent;
		border-bottom: 1px solid transparent;
		border-radius: 6px 6px 0 0;
		font-weight: 600;
  	}

	.tab.active {
		background: var(--color-neutral-100);
		border-color: var(--color-neutral-300);
		border-bottom-color: transparent;
	}

	.back-link {
		font-size: 0.9rem;
	}

	.edit-user-page {
		width: 100%;
		max-width: 900px;
		display: grid;
		gap: 1rem;
	}

	.card {
		border: 1px solid var(--color-neutral-400);
		border-radius: var(--radius-md);
		padding: 1rem;
		display: grid;
		gap: 0.75rem;
		background-color: var(--color-neutral-100);
	}

	.post-actions {
		display: flex;
		gap: 1rem;
	}
</style>