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
				href="./"
				class="tab"
				class:active={true}
				>Profile</a
			>
  			<a href="./{data.user.id}/posts" class="tab" class:active={false}>Posts</a>
  			<a href="./{data.user.id}/comments" class="tab" class:active={false}>Comments</a>
		</nav>

	{#if form?.message}
		<p class:success={form.success} class:error={!form.success}>{form.message}</p>
	{/if}

	<section class="card">
		<h2>Core details</h2>
		<form method="POST" action="?/updateUserCore" class="form-grid">			
			<label>
				First name
				<input name="firstName" value={data.user.first_name ?? ''} />
			</label>

			<label>
				Last name
				<input name="lastName" value={data.user.last_name ?? ''} />
			</label>

			<label>
				Username
				<input name="username" value={data.user.name} required />
			</label>

			<label>
				Email
				<input name="email" type="email" value={data.user.email} required />
			</label>

			<label class="full-width">
				Image URL
				<input name="image" value={data.user.image ?? ''} />
			</label>

			<label class="full-width">
				Biography
				<textarea name="biography" rows="5">{data.user.biography ?? ''}</textarea>
			</label>

			<label class="full-width">
				Interests
				<input name="interests" value={data.user.interests ?? ''} />
			</label>

			<label>
				Role
				<select name="role" value={data.user.role}>
					<option value="USER">USER</option>
					<option value="MODERATOR">MODERATOR</option>
					<option value="ADMIN">ADMIN</option>
				</select>
			</label>

			<div class="timestamps">
				<div><strong>Joined:</strong> {formatDate(data.user.createdAt)}</div>
				<div><strong>Last update:</strong> {formatDate(data.user.updatedAt)}</div>
			</div>

			<button type="submit" class="full-width">Save core details</button>
		</form>
	</section>
		
	<form method="POST" action="?/deleteUser" onsubmit={confirmDelete}>
		<button type="submit" class="full-width" style="background-color: red;">Delete account</button>
	</form>

	<section class="card">
		<h2>User posts (read-only)</h2>
		{#if data.posts.length === 0}
			<p>This user has no posts.</p>
		{:else}
			<ul class="posts-list">
				{#each data.posts as post}
					<li>
						<span>{post.title}</span>
						<small>
							#{post.id} • {formatDate(post.created_at)}{post.deleted_at ? ' • deleted' : ''}
						</small>
					</li>
				{/each}
			</ul>
		{/if}
	</section>
</div>

<style>
	.edit-user-page {
		width: 100%;
		max-width: 900px;
		display: grid;
		gap: 1rem;
	}

	.back-link {
		font-size: 0.9rem;
	}

	h1,
	h2 {
		margin: 0;
	}

	.card {
		border: 1px solid var(--color-neutral-400);
		border-radius: var(--radius-md);
		padding: 1rem;
		display: grid;
		gap: 0.75rem;
		background-color: var(--color-neutral-100);
	}

	.form-grid {
		display: grid;
		gap: 0.75rem;
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}

	label {
		display: grid;
		gap: 0.3rem;
		font-size: 0.9rem;
	}

	input,
	select,
	textarea,
	button {
		font: inherit;
		padding: 0.5rem 0.6rem;
		border-radius: 0.4rem;
		border: 1px solid var(--color-neutral-400);
	}

	button {
		cursor: pointer;
		font-weight: 600;
	}

	.full-width {
		grid-column: 1 / -1;
	}

	.timestamps {
		display: grid;
		gap: 0.2rem;
		font-size: 0.9rem;
		align-content: end;
	}

	.posts-list {
		margin: 0;
		padding-left: 1rem;
		display: grid;
		gap: 0.35rem;
	}

	.posts-list li {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
	}

	.posts-list small {
		color: var(--color-text-secondary);
	}

	.success {
		color: green;
		margin: 0;
	}

	.error {
		color: red;
		margin: 0;
	}

	@media (max-width: 720px) {
		.form-grid {
			grid-template-columns: 1fr;
		}

		.posts-list li {
			flex-direction: column;
			gap: 0.2rem;
		}
	}

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
</style>
