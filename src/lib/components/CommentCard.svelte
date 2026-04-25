<script lang=ts>
    import { goto } from '$app/navigation';

	let rawProps = $props() as { comment: any };
    let comment = $derived(rawProps.comment);

	function openProfile() {
        goto(`/profile/${comment.user.name}`);
    }
</script>

<div>
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
			<enhanced:img
                src={comment.image || `https://placehold.co/300x300/white/black.webp?text=404+Not+Found`}
                onerror={(e) => { (e.target as HTMLImageElement).src = `https://placehold.co/300x300/white/black.webp?text=404+Not+Found`; }}
				alt="Comment attachment"
                class="card-img"
            />
		{/if}
  	</div>
</div>
