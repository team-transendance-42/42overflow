<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import CommentCard from '$lib/components/CommentCard.svelte';
	import CreateComment from '$lib/components/CreateComment.svelte';
	import PostCard from '$lib/components/PostCard.svelte';

	// Define types for post and comments
	type Comment = {
		id: number;
		content: string;
		image?: string | null;
		likeCount: number;
		created_at: Date | string;
		user: { name: string; id: string; };
		children?: Comment[];
	};
	type Post = {
		id: number;
		title: string;
		content: string;
		user: { name: string; id: string; };
		comments?: Comment[];
	};

	// Get data from props with inline type
	interface PageData {
		post: Post | null;
	}

	let { data } = $props() as any as { data: PageData };
	let post = data.post;
	let comments = $state<Comment[]>([]);

	onMount(() => {
		if (!post?.id) return;

		comments = data.post?.comments ?? [];

		const source = new EventSource(
			`/api/posts/${post.id}/comments/stream`
		);

		source.onmessage = (event) => {
			const data = JSON.parse(event.data);

			if (data.type === 'comment-create') {
				comments = [...comments, data.comment];
				return;
			}

			if (data.type === 'comment-update') {
				comments = comments.map(c =>
					c.id === data.comment.id ? data.comment : c
				);
				return;
			}

			if (data.type === 'like-update') {
				comments = comments.map(c =>
					c.id === data.commentId
						? { ...c, likeCount: data.likeCount, userLiked: data.userLiked }
						: c
				);
				return;
			}
		};

		return () => source.close();
	});

	let postId = $derived(post?.id ?? 0);

	function openProfile() {
        goto(`/profile/${post?.user.name}`);
    }
</script>

<!-- Post with Comments -->
<div>
	{#if post}
		<PostCard {post} />

		<!-- Create Comment under Post -->
		<CreateComment {postId} />

		<!-- Show all Comments -->
		{#each comments as comment (comment.id)}
			<CommentCard {comment} />
		{/each}
	{/if}
</div>
