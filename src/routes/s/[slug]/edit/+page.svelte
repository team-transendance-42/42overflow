<script lang="ts">
	import { type SubjectDescriptionInput, SubjectDescriptionSchema } from '$lib/zodTypes';
	import { z } from 'zod';

	interface Props {
		data: {
			subject: {
				id: number;
				name: string;
				slug: string;
				description?: string;
				memberships: {
					userId: number;
					subjectId: number;
					role: 'admin' | 'member';
				}[];
			}
		};
	}

	let { data }: Props = $props();
	let derivedDescription = $derived(data.subject?.description ?? '');

	let formData = $state<SubjectDescriptionInput>({
		description: ''
	});

	$effect(() => {
		formData.description = derivedDescription;
	});

	let errors = $state({} as Record<string, string[]>);
	let isSubmitting = $state(false);

	// Real-time validation on single input field
    function handleInput<K extends keyof SubjectDescriptionInput>(field: K, value: SubjectDescriptionInput[K]) {
        // update the reactive $state object in-place instead of replacing it
        (formData as any)[field] = value;
        try {
            SubjectDescriptionSchema.pick({ [field]: true } as any).parse({ [field]: value } as any);
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
            SubjectDescriptionSchema.parse(postData);

            // Create FormData for file upload
            const formDataToSend = new FormData();
            Object.entries(postData).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    formDataToSend.append(key, value.toString());
                }
            });

            const response = await fetch(`/api/subjects/${data.subject.slug}/edit`, {
                method: 'POST',
                body: formDataToSend
            });

            if (response.ok) {
                // Redirect to posts page after successful creation
                window.location.reload();
            } else {
                alert('An error occurred while creating the post. Please try again.');
            }
        } catch (err) {
			if (err instanceof z.ZodError) {
				errors = z.flattenError(err).fieldErrors;
				return;
			}

			alert('An error occurred while creating the post. Please try again.');
			console.error('Unexpected error submitting:', err);
		} finally {
			isSubmitting = false;
		}
    }
</script>

<form onsubmit={handleSubmit}>
	<div>
		<h1>Edit {data.subject.name}</h1>

		<label for="description">Description</label>
		<textarea
			class="input-group"
			name="description"
			id="description"
			placeholder="Describe the subject..."
			bind:value={formData.description}
			oninput={(event) => handleInput('description', (event.target as HTMLTextAreaElement).value)}
			rows={5}
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
</style>
