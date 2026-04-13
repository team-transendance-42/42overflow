<script lang="ts">
	type UserListItem = {
		id: string;
		name: string | null;
		email?: string;
		role: 'USER' | 'MODERATOR' | 'ADMIN';
		image: string | null;
		createdAt: string | Date;
	};

	let { data }: { data: { users: UserListItem[]; canViewEmail: boolean } } = $props();

	function formatDate(value: string | Date) {
		return new Date(value).toLocaleDateString();
	}
</script>

<div class="users-page">
	<h1>Users</h1>

	{#if data.users.length === 0}
		<p>No users found.</p>
	{:else}
		<div class="users-list">
			{#each data.users as user}
				<article class="user-card">
					<div class="user-main">
						{#if user.image}
							<img src={user.image} alt={user.name ?? 'User avatar'} class="avatar" />
						{/if}
						<div>
							<h2>{user.name ?? 'Unnamed user'}</h2>
							<p class="email-row">
								<span class="email-label">Email:</span>
								<span class="email-value">{data.canViewEmail && user.email ? user.email : null}</span>
							</p>
						</div>
					</div>
					<div class="user-meta">
						<span class="role">{user.role}</span>
						<span>Joined {formatDate(user.createdAt)}</span>
					</div>
				</article>
			{/each}
		</div>
	{/if}
</div>

<style>
	.users-page {
		width: 100%;
		max-width: 900px;
		padding: 0;
		text-align: left;
	}

	.users-list {
		display: grid;
		gap: 0.75rem;
	}

	.user-card {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.9rem;
		border: 1px solid var(--color-neutral-400);
		border-radius: var(--radius-md);
		background-color: var(--color-neutral-100);
	}

	.user-main {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
	}

	.avatar {
		width: 42px;
		height: 42px;
		border-radius: 999px;
		object-fit: cover;
		border: 1px solid var(--color-neutral-400);
	}

	.user-main h2 {
		margin: 0;
		font-size: 1rem;
	}

	.email-row {
		margin: 0.15rem 0 0;
		font-size: 0.9rem;
		display: flex;
		gap: 0.3rem;
	}
	.email-label {
		font-weight: 600;
	}
	.email-value {
		min-width: 12ch; /* keeps layout stable for moderators */
	}

	.user-main p {
		margin: 0.15rem 0 0;
		font-size: 0.9rem;
	}

	.user-meta {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.3rem;
		font-size: 0.85rem;
	}

	.role {
		display: inline-block;
		padding: 0.1rem 0.5rem;
		border: 1px solid var(--color-neutral-500);
		border-radius: var(--radius-sm);
		font-weight: 700;
	}

	@media (max-width: 720px) {
		.user-card {
			flex-direction: column;
			align-items: flex-start;
			gap: 0.6rem;
		}

		.user-meta {
			align-items: flex-start;
		}
	}
</style>
