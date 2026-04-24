<script lang=ts>
	import Textarea from '$lib/components/Textarea.svelte';

	let rawProps = $props() as { parentId: any; postId: any };
    // let parentId = $derived(rawProps.parentId);
	// let postId = $derived(rawProps.postId);
	let parentId = 1;
	let postId = 1;

	let body = $state("");
	let error = $state("");

	async function submitComment() {
		if (!body) {
			error = "You can't submit an empty comment.";
			return;
		}

		const res = await fetch(`/api/posts/${1}/comments/create`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				parentId,
				body
			})
		});

		if (res.ok) {
			window.location.reload();
		} else if (res.status === 401) {
			error = "You must be logged in to post a comment.";
		} else {
			console.log(res);
			error = "Something went wrong, please try again.";
		}
	}
</script>

<div class="post-comment">
	{#if error}
		<p class="error">{error}</p>
	{/if}

	<Textarea
		label="Comment"
		name="body paragraph"
		placeholder="Write your comment here..."
		bind:value={body}
		rows={5}
	/>

	<button onclick={submitComment}>Submit</button>
</div>

<style>
  .post-comment {
    width: 100%;
    max-width: 700px;
    padding: 0rem;
    text-align: left;
  }
  .error {
    color: red;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
  }
</style>