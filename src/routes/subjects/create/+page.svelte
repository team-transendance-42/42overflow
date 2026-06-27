<script lang="ts">
	import { goto } from '$app/navigation';
	import { type CreateSubjectInput, CreateSubjectSchema } from '$lib/zodTypes';
	import { z } from 'zod';

    let errors = $state({} as Record<string, string[]>);
	let isSubmitting = $state(false);

	let formData = $state<CreateSubjectInput>({
		name: '',
		description: ''
	});

	// Real-time validation on single input field
    function handleInput<K extends keyof CreateSubjectInput>(field: K, value: CreateSubjectInput[K]) {
        // update the reactive $state object in-place instead of replacing it
        (formData as any)[field] = value;
        try {
            CreateSubjectSchema.pick({ [field]: true } as any).parse({ [field]: value } as any);
            const key = field as string;
            if (errors[key]) {
                delete errors[key];
                errors = { ...errors };
            }
        } catch (err) {
            if (err instanceof z.ZodError) {
				const fieldErrors = z.flattenError(err).fieldErrors;

				errors = fieldErrors;
				return;
			}
			console.error('Unexpected error:', err);
        }
    }

	// Handle form submission
    async function handleSubmit(event: Event) {
        if (isSubmitting) return; // Prevent multiple submissions
        event.preventDefault();
        isSubmitting = true;
        errors = {};

        try {
            // Validate form data (excluding image)
            const { ...postData } = formData;
            CreateSubjectSchema.parse(postData);

            // Create FormData for file upload
            const formDataToSend = new FormData();
            Object.entries(postData).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    formDataToSend.append(key, value.toString());
                }
            });

            const response = await fetch(`/api/subjects/create`, {
                method: 'POST',
                body: formDataToSend
            });

            if (response.ok) {
                // Redirect to subjects page after successful creation
                goto('/subjects');
            } else {
                alert('An error occurred while creating the subject. Please try again.');
            }
        } catch (err) {
			if (err instanceof z.ZodError) {
				errors = z.flattenError(err).fieldErrors;
				return;
			}

			alert('An error occurred while creating the subject. Please try again.');
			console.error('Unexpected error submitting:', err);
		} finally {
			isSubmitting = false;
		}
    }
</script>


<form onsubmit={handleSubmit}>
	<div>
		<h1>Create a subject</h1>

		<label for="name">Name</label>
		<input
			class="input-group"
			placeholder="Name"
			id="name"
			bind:value={formData.name}
			oninput={(event) => handleInput('name', (event.target as HTMLTextAreaElement).value)}
			required
		/>
		{#if errors.name}
			<p class="error">{errors.name[0]}</p>
		{/if}

		<label for="description">Description</label>
		<textarea
			class="input-group"
			placeholder="Description"
			id="description"
			bind:value={formData.description}
			oninput={(event) => handleInput('description', (event.target as HTMLTextAreaElement).value)}
			rows="3"
		></textarea>
		{#if errors.description}
			<p class="error">{errors.description[0]}</p>
		{/if}

		{#if isSubmitting}
			<button type="button" class="button primary" disabled>
				Submitting...
			</button>
		{:else}
			<button type="submit" class="button confirm">
				Confirm
			</button>
		{/if}
	</div>
</form>
