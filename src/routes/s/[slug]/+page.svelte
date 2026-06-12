<script lang="ts">
	import {page} from '$app/stores';
	import type { ComponentProps } from 'svelte';
	import PostCard from '$lib/components/PostCard.svelte';
	import { onMount } from 'svelte';

	type Post = ComponentProps<typeof PostCard>['post'];
	
	let title = '';
	let content = '';
	let message = '';
	let error = '';

	let questions: Post[] = [];
	let currentPage = 1;
	let limit = 5;
	let total = 0;

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		message = '';
		error = '';

		const res = await fetch(`/api/subjects/${$page.params.slug}/post`, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({ title, content })
		});

		await loadSubject();
	}

	async function loadSubject() {
		const res = await fetch(`/api/subjects/${$page.params.slug}/post?page=${currentPage}&limit=${limit}`);
		const json = await res.json();

		questions = (json.data ?? []) as Post[];
		total = json.total;
	};

	onMount(loadSubject);		

</script>

<!-- Posts -->
<div>
	<h1><strong>
		NEWEST QUESTIONS
	</strong></h1>

	{#each questions as post}
		<PostCard {post} />
	{/each}
</div>

<!-- Pagination -->
<div>
	<button on:click={() => {
		if (currentPage > 1) {
			currentPage--;
			loadSubject();
		}
	}}>
	Prev
	</button>

	<span> - Page {currentPage} -</span>

	<button on:click={() => {
		if (currentPage * limit < total) {
			currentPage++;
			loadSubject();
		}
	}}>
	Next
	</button>
</div>


<div>
	<h1><strong>CREATE A POST</strong></h1>

	<form on:submit={handleSubmit}>
		<div>
			<label>
				<div>Title</div>
				<input bind:value={title} required />
			</label>
		</div>
		<div>
			<label>
				<div>Content</div>
				<textarea bind:value={content} rows="3"></textarea>
			</label>
		</div>

		<button type="submit">submit</button>
	</form>
</div>