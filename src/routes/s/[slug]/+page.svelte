<script lang="ts">
import {page} from '$app/stores';

	let title = '';
	let content = '';
	let message = '';
	let error = '';

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		message = '';
		error = '';

		const res = await fetch(`/api/subjects/${$page.params.slug}/post`, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ title, content })
		});
	}

</script>

<div>
	<h1>Create a post</h1>

	<form on:submit={handleSubmit}>
		<label>
			Title
			<input bind:value={title} required />
		</label>

		<label>
			Content
			<textarea bind:value={content} rows="3"></textarea>
		</label>

		<button type="submit">submit</button>
	</form>
</div>