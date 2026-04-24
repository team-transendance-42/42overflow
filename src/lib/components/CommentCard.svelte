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
		<p>{comment.content}</p>

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
  	</div>
</div>
