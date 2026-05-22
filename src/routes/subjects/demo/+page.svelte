<script lang="ts">
	let name = '';
	let description = '';
	let message = '';
	let error = '';
	let slug = '';

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		message = '';
		error = '';

		const res = await fetch('/api/subjects/create', {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ name, description })
		});

		if (!res.ok) {
			const text = await res.text();
			error = text || 'Failed to create subject';
			return;
		}

		const subject = await res.json();
		message = `Created subject: ${subject.name}`;
		name = '';
		description = '';
	}

	async function handleArchive(e: SubmitEvent) {
		e.preventDefault();
		message = '';
		error = '';

		const res = await fetch('/api/subjects/archive', {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ slug })
		});

		if (!res.ok) {
			const text = await res.text();
			error = text || 'Failed to archive subject';
			return;
		}

		const subject = await res.json();
		message = `Archived subject: ${subject.name}`;
		name = '';
		description = '';
	}

	async function handleSubscribe(e: SubmitEvent) {
		e.preventDefault();
		message = '';
		error = '';

		const res = await fetch(`/api/subjects/${encodeURIComponent(slug)}/subscriptions`, {
			method: 'POST'
		});

		if (!res.ok) {
			error = (await res.text()) || 'Failed to subscribe';
			return;
		}

		message = 'Subscribed';
	}

	async function handleUnsubscribe(e: SubmitEvent) {
		e.preventDefault();
		message = '';
		error = '';

		const res = await fetch(`/api/subjects/${encodeURIComponent(slug)}/subscriptions`, {
			method: 'DELETE'
		});

		if (!res.ok) {
			error = (await res.text()) || 'Failed to unsubscribe';
			return;
		}

		message = 'Unsubscribed';
	}
</script>

<div>
	<h1>Create a subject</h1>

	<form on:submit={handleSubmit}>
		<label>
			Name
			<input bind:value={name} required />
		</label>

		<label>
			Description
			<textarea bind:value={description} rows="3"></textarea>
		</label>

		<button type="submit">Create</button>
	</form>
</div>

{#if message}<p class="success">{message}</p>{/if}
{#if error}<p class="error">{error}</p>{/if}

<div>
	<h1>Archive a subject</h1>

	<form on:submit={handleArchive}>
		<label>
			Slug
			<input bind:value={slug} required />
		</label>

		<button type="submit">Archive</button>
	</form>
</div>

<div>
	<h1>Subscribe to a subject</h1>

	<form on:submit={handleSubscribe}>
		<label>
			Slug
			<input bind:value={slug} required />
		</label>

		<button type="submit">Subscribe</button>
	</form>
</div>

<div>
	<h1>Unsubscribe from a subject</h1>

	<form on:submit={handleUnsubscribe}>
		<label>
			Slug
			<input bind:value={slug} required />
		</label>

		<button type="submit">Unsubscribe</button>
	</form>
</div>

<style>
	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		max-width: 400px;
	}

	label {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.success {
		color: green;
	}

	.error {
		color: red;
	}
</style>
