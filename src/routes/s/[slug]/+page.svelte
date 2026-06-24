<script lang="ts">
	import {page} from '$app/stores';
	import type { ComponentProps } from 'svelte';
	import PostCard from '$lib/components/PostCard.svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let { data } = $props();

	type Post = ComponentProps<typeof PostCard>['post'];

	let questions: Post[] = $state([]);
	let currentPage = $state(1);
	let limit = 5;
	let total = 0;
	let hasPermission: boolean = data.hasPermission ? true : false;

	async function loadSubject() {
		const res = await fetch(`/api/subjects/${$page.params.slug}/post?page=${currentPage}&limit=${limit}`);
		const json = await res.json();

		if (!res.ok) {
			error = json.error || 'An error occurred while loading posts.';
			return;
		}

		questions = (json.data ?? []) as Post[];
		total = json.total;
	};

	function makePost() {
		goto(`/post-question?subject=${data.subject.name}`);
	}

	onMount(loadSubject);

</script>

<div class=posts-page>
	<div class="subject-header">
		<h1><strong>{data.subject.name}</strong></h1>
		<p>{data.subject.description ? data.subject.description : 'No description available.'}</p>
	</div>

	<!-- Posts -->
	{#each questions as post}
		<PostCard {post} {hasPermission} />
	{/each}

	<div class="mb-4">
		<button class="button primary" onclick={makePost}>Create Post</button>
	</div>

	<!-- Pagination -->
	<div>
		<button onclick={() => {
			if (currentPage > 1) {
				currentPage--;
				loadSubject();
			}
		}}>
			Prev
		</button>

		<span> - Page {currentPage} -</span>

		<button onclick={() => {
			if (currentPage * limit < total) {
				currentPage++;
				loadSubject();
			}
		}}>
			Next
		</button>
	</div>
</div>
