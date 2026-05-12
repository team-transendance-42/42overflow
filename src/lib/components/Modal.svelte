<script>
	let { showModal = $bindable(), header, children } = $props();

	// HTMLDialogElement
	let dialog = $state();

	$effect(() => {
		if (showModal) dialog.showModal();
	});
</script>

<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
<dialog
	bind:this={dialog}
	onclose={() => (showModal = false)}
	onmousedown={(e) => { if (e.target === dialog) dialog.close(); }}
>
	<div>
		{@render header?.()}
		<hr />
		{@render children?.()}
		<hr />
		<!-- svelte-ignore a11y_autofocus -->
		<button class="btn btn-md btn-secondary btn-codam mt-4" autofocus onclick={() => dialog.close()}>Cancel</button>
	</div>
</dialog>
