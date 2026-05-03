<script lang=ts>
    import { goto } from '$app/navigation';
    import CommentCard from './CommentCard.svelte';
	import CreateComment from './CreateComment.svelte';

	interface Props {
		comment: any;
		depth?: number;
	}

	let { comment, depth = 0 }: Props = $props();

	// Derive postId and parentId for creating replies to this comment
	let postId = $derived(comment.postId);
	let parentId = $derived(comment.id);

	async function deleteComment() {
		if (!confirm('Are you sure you want to delete this comment?')) {
			return;
		}
		const response = await fetch(`/api/posts/${postId}/comments/${comment.id}/delete`, {
			method: 'POST',
		});

		if (!response.ok) {
			const errorData = await response.json();
			console.error('Failed to delete comment:', errorData);
			alert('Failed to delete comment: ' + (errorData.message || 'Unknown error'));
			return;
		}

		console.log(`Delete comment with ID: ${comment.id}`);
		// Refresh the page or remove the comment from the UI
		window.location.reload();
	}

	function openProfile() {
        goto(`/profile/${comment.user.name}`);
    }
</script>

<div style="margin-left: {depth * 20}px;">
	<div class=postbox>
		<!-- View Profile Button -->
		<button
			class="bg-sky-500 hover:bg-sky-700"
			onclick={openProfile}
			aria-label="View {comment.user.name}'s profile'"
		>
			<p class="author">
				{#if comment.deleted_at}
					[Deleted User]
				{:else}
					Posted by: {comment.user.name}
				{/if}
			</p>
		</button>

		<!-- Comment Content -->
		<p>{comment.content}</p>

		<!-- Comment Image (Optional) -->
		{#if comment.image}
			<img
                src={comment.image || `https://placehold.co/300x300/white/black.webp?text=404+Not+Found`}
                onerror={(e) => { (e.target as HTMLImageElement).src = `https://placehold.co/300x300/white/black.webp?text=404+Not+Found`; }}
				alt="Comment attachment"
                class="card-img"
            />
		{/if}

		<!-- Reply to Comment -->
		<CreateComment {postId} {parentId} />

		<!-- Delete Comment -->
		<button
			class="bg-red-500 hover:bg-red-700"
			onclick={deleteComment}
			aria-label="Delete comment"
		>
			Delete
		</button>

  	</div>

	<!-- Render nested children/replies -->
	{#if comment.children && comment.children.length > 0}
		{#each comment.children as child}
			<CommentCard comment={child} depth={depth + 1} />
		{/each}
	{/if}
</div>
