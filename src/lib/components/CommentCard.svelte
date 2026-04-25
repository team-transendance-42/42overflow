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
				Posted by: {comment.user.name}
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

  	</div>

	<!-- Render nested children/replies -->
	{#if comment.children && comment.children.length > 0}
		{#each comment.children as child}
			<CommentCard comment={child} depth={depth + 1} />
		{/each}
	{/if}
</div>
