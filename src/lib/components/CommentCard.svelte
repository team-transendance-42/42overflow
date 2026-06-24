<script lang=ts>
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
    import CommentCard from './CommentCard.svelte';
	import CreateComment from './CreateComment.svelte';
	import EditComment from './EditComment.svelte';

	interface Props {
		comment: any;
		depth?: number;
	}

	let { comment, depth = 0 }: Props = $props();

	// Derive postId and parentId for creating replies to this comment
	const postId = comment.postId;
	const parentId = comment.id;
	let isOwn = $derived.by(() => page.data.user?.id === comment.userId);

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

	async function likeComment() {
		// Toggle like/unlike based on current state
		const response = await fetch(`/api/posts/${postId}/comments/${comment.id}/${comment.userLiked ? 'unlike' : 'like'}`, {
			method: 'POST',
		});

		if (!response.ok) {
			const errorData = await response.json();
			console.error(`Failed to ${comment.userLiked ? "unlike" : "like"} comment:`, errorData);
			alert(`Failed to ${comment.userLiked ? "unlike" : "like"} comment: ${errorData.message || 'Unknown error'}`);
			return;
		}

		console.log(`Comment with ID: ${comment.id} ${comment.userLiked ? 'unliked' : 'liked'}`);
		window.location.reload();
	}

	function openProfile() {
        goto(`/profile/${comment.user.name}`);
    }
</script>

<div class="commentbox clickable relative" style="margin-left: {depth * 30}px; width: calc(100% - {depth * 30}px);">
	{#if comment.isEdited}
		<div class="break-all line-clamp-1"><em>[Edited]</em></div>
	{/if}

	<!-- Comment Content -->
	<div class="break-all">{comment.content}</div>

	<!-- Comment Image (Optional) -->
	{#if comment.image}
		<img
			src={comment.image || `https://placehold.co/300x300/white/black.webp?text=404+Not+Found`}
			onerror={(e) => { (e.target as HTMLImageElement).src = `https://placehold.co/300x300/white/black.webp?text=404+Not+Found`; }}
			alt="Comment attachment"
			class="card-img"
		/>
	{/if}

	<!-- Buttons -->
	<div class="comment-actions">
		<!-- View Profile Button -->
		{#if comment.deleted_at == null}
			<button
				class="button postcard clickable"
				onclick={openProfile}
				aria-label="View {comment.user.name}'s profile'"
			>
				<p class="author">
					Author: <em>{comment.user.name}</em>
				</p>
			</button>
		{:else}
			<div class="button postcard">
				<p class="author">
					<em>[anonymous]</em>
				</p>
			</div>
		{/if}

		<!-- Reply to Comment -->
		{#if comment.deleted_at == null}
			<CreateComment {postId} {parentId} />
		{/if}

		<!-- Edit Comment -->
		{#if isOwn && comment.deleted_at == null}
			<EditComment {postId} {comment} />
		{/if}

		<!-- Delete Comment -->
		{#if isOwn && comment.deleted_at == null}
			<button
				class="button postcard delete clickable"
				onclick={deleteComment}
				aria-label="Delete comment"
			>
				Delete
			</button>
		{/if}

		<!-- Like Button -->
		<button
			class="button postcard like clickable"
			onclick={likeComment}
			aria-label="Like comment"
		>
			{(comment.userLiked ? '♥ ' : '♡ ') + (comment.likeCount ?? 0)}
		</button>
	</div>
</div>

<!-- Render nested children/replies -->
{#if comment.children && comment.children.length > 0}
	{#each comment.children as child}
		<CommentCard comment={child} depth={depth + 1} />
	{/each}
{/if}
