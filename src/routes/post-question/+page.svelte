<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { type CreatePostInput, CreatePostSchema } from '$lib/zodTypes';
	import { z } from 'zod';

	interface Props {
		data: {
			subjectList: {
				id: number;
				name: string;
			}[];
		};
	}

	let { data }: Props = $props();
	let subjectList = $derived(data.subjectList ?? []);

    let errors = $state({} as Record<string, string[]>);
	let isSubmitting = $state(false);

	let formData = $state<CreatePostInput>({
		title: '',
		subjectId: 0,
		content: ''
	});

	$effect(() => {
		formData.subjectId = subjectList.find(s => s.name === (page.url.searchParams.get('subject') || ''))?.id ?? 0;
	});

	// Real-time validation on single input field
    function handleInput<K extends keyof CreatePostInput>(field: K, value: CreatePostInput[K]) {
        // update the reactive $state object in-place instead of replacing it
        (formData as any)[field] = value;
        try {
            CreatePostSchema.pick({ [field]: true } as any).parse({ [field]: value } as any);
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
            CreatePostSchema.parse(postData);

            // Create FormData for file upload
            const formDataToSend = new FormData();
            Object.entries(postData).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    formDataToSend.append(key, value.toString());
                }
            });

            const response = await fetch(`/api/posts/create`, {
                method: 'POST',
                body: formDataToSend
            });

            if (response.ok) {
                // Redirect to posts page after successful creation
                goto('/posts');
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
		<h1>ASK A QUESTION</h1>

		<label for="title">Title</label>
		<input
			class="input-group"
			placeholder="Title"
			id="title"
			bind:value={formData.title}
			oninput={(event) => handleInput('title', (event.target as HTMLTextAreaElement).value)}
		/>
		{#if errors.title}
			<p class="error">{errors.title[0]}</p>
		{/if}

		<div class="dropdown-group">
			<label for="subject-selector">Subject</label>
			<select
				class="black-text"
				bind:value={formData.subjectId}
			>
				<option value={0} disabled>Select a subject</option>

				{#each subjectList as subjectOption}
					<option value={subjectOption.id}>
						{subjectOption.name}
					</option>
				{/each}
			</select>
		</div>

		<label for="content">Content</label>
		<textarea
			class="input-group"
			name="content"
			id="content"
			placeholder="Write your question in detail here..."
			bind:value={formData.content}
			oninput={(event) => handleInput('content', (event.target as HTMLTextAreaElement).value)}
			rows={5}
		></textarea>
		{#if errors.content}
			<p class="error">{errors.content[0]}</p>
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
