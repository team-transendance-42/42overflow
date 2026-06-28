<script lang="ts">
	import { goto } from "$app/navigation";

	export let subject: {
		id: number;
		name: string;
		slug: string;
		description: string;
		created_at: Date;
		memberCount: number;
		postCount: number;
		isMember: boolean;
		isOwner: boolean;
	};
	export let isLoggedIn = false;
	export let isOwner = false;
	let isMember = subject.isMember;
	
	let errorMessage = '';

	const formatDate = (date: Date) => {
		return new Date(date).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	};

	async function subscribe(event: MouseEvent) {
    event.preventDefault();

    const res = await fetch(`/api/subjects/${encodeURIComponent(subject.slug)}/subscriptions`, {
      method: 'POST'
    });

    if (!res.ok) {
      const data = await res.json();
	  errorMessage = data.error || 'An error occurred while subscribing.';
      console.error('Subscribe failed');
      return;
    }
	isMember = true;
	window.location.reload();
  }

  async function unsubscribe(event: MouseEvent) {
    event.preventDefault();

    const res = await fetch(`/api/subjects/${encodeURIComponent(subject.slug)}/subscriptions`, {
      method: 'DELETE'
    });

    if (!res.ok) {
      const data = await res.json();
	  errorMessage = data.message || 'An error occurred while unsubscribing.';
      console.error('Unsubscribe failed');
      return;
	}
	isMember = false;
	window.location.reload();
  }
</script>

<div class="subject-box">
	<a class="card-link" href={`/s/${subject.slug}`} aria-label={'Open subject ' + subject.name}></a>
	<div class="name-header">
		<h2>{subject.name}</h2>
		<p class="slug">/s/{subject.slug}</p>
	</div>
	{#if subject.description}
		<p class="description">{subject.description}</p>
	{/if}

	<div class="metadata">
		<div class="meta-item">
			<span class="label">Members:</span>
			<span class="value">{subject.memberCount}</span>
		</div>
		<div class="meta-item">
			<span class="label">Posts:</span>
			<span class="value">{subject.postCount}</span>
		</div>
		<div class="meta-item">
			<span class="label">Created:</span>
			<span class="value">{formatDate(subject.created_at)}</span>
		</div>
	</div>

	<div class="actions">
		{#if !isLoggedIn}
			<a class="button subscribe" href="/login">Subscribe</a>
		{:else if isMember}
			<button class="button unsubscribe" on:click={unsubscribe}>Unsubscribe</button>
		{:else}
			<button class="button subscribe" on:click={subscribe}>Subscribe</button>
		{/if}

		{#if isOwner}
			<a class="button manage" href={`/s/${subject.slug}/manage`}>Manage</a>
		{/if}
	</div>
	{#if errorMessage}
		<p class="error-message">{errorMessage}</p>
	{/if}
</div>

<style>

	.error-message {
		color: red;
		font-size: 0.9rem;
		margin-top: 0.5rem;
		border: 1px solid red;
		padding: 0.5rem;
		border-radius: 4px;
		background-color: #ffe6e6;
	}
	.actions {
		display: flex;
		gap: 0.5rem;
		align-items: center;
		margin-top: 0.5rem;
	}
	.subject-box {
		position: relative;
		border: 1px solid var(--color-neutral-400);
		border-radius: var(--radius-md);
		padding: 0.9rem;
		background: var(--color-neutral-100);
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		max-width: 600px;
	}
	.card-link {
		position: absolute;
		inset: 0;
		z-index: 1;
	}
	.name-header {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.name-header h2 {
		margin: 0;
	}

	.name-header .slug {
		margin: 0;
	}

	h2 {
		margin: 0;
		font-size: 1.25rem;
	}

	.slug {
		margin: 0;
		font-size: 0.9rem;
	}

	.description {
		margin: 0;
		font-size: 0.95rem;
		line-height: 1.4;
	}

	.metadata {
		display: flex;
		gap: 1.5rem;
		font-size: 0.9rem;
		padding-top: 0.5rem;
	}

	.meta-item {
		display: flex;
		flex-direction: row;
		gap: 0.25rem;
	}

	.label {
		font-weight: 500;
	}

	.value {
		font-weight: 600;
	}
</style>
