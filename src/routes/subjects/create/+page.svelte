<script lang="ts">
	let name = '';
	let description = '';
	let message = '';
	let error = '';

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