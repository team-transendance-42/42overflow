<script lang="ts">
  import { onMount } from 'svelte';
  import type { ComponentProps } from 'svelte';
  import PostCard from '$lib/components/PostCard.svelte';

	type Post = ComponentProps<typeof PostCard>['post'];

	let questions: Post[] = [];
	let page = 1;
	let limit = 10;
	let total = 0;

	async function loadQuestions() {
		const res = await fetch(`/api/questions?page=${page}&limit=${limit}`);
		const json = await res.json();

		questions = (json.data ?? []) as Post[];
		total = json.total;
	};

	onMount(loadQuestions);
</script>

<div class="questions-page">
	<h1><strong>
		NEWEST QUESTIONS
	</strong></h1>

	{#each questions as post}
		<PostCard {post} />
	{/each}
</div>

<div class="pagination">
	<button on:click={() => {
		if (page > 1) {
			page--;
			loadQuestions();
		}
	}}>
	Prev
	</button>

	<span> - Page {page} -</span>

	<button on:click={() => {
		if (page * limit < total) {
			page++;
			loadQuestions();
		}
	}}>
	Next
	</button>
</div>
