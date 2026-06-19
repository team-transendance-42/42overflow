<script lang="ts">
	import type { PageData, ActionData } from './$types';

	export let data: PageData;
    export let form: ActionData;

	$: ({ subject } = data);
</script>

<div>
	<h1>Edit {subject.name}</h1>

	<form method="POST">
		<label>
			Description
			<textarea
				name="description"
				rows="4"
			>{subject.description || ''}</textarea>
		</label>
        {#if form?.error}
            <p class="error">{form.error}</p>
        {/if}
		<button
			type="submit"
		>
			Save
		</button>
	</form>
</div>
<style>
	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		max-width: 400px;
	}

	label {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.error {
		color: red;
	}
</style>
