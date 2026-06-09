<script lang=ts>
    import Modal from '$lib/components/Modal.svelte';
    import { CommentSchema } from '$lib/zodTypes.js';
    import type { CommentInput } from '$lib/zodTypes.js';
    import { z } from 'zod';

    let showModal = $state(false);

    interface Props {
        postId: number;
        parentId?: number;
        comment: any;
    }

    let { postId, parentId, comment }: Props = $props();
    let derivedPostId = $derived(postId);
    let derivedParentId = $derived(parentId ?? undefined);
    let removeImage = $state(false);

    type CommentFormInput = CommentInput & {
        image?: File;
    };

    let formData = $state<CommentFormInput>({
        postId: 0,
        parentId: undefined,
        content: '',
    });

    let previewUrl = $state<string>('');

    $effect(() => {
        formData.postId = derivedPostId;
        formData.parentId = derivedParentId;
        formData.content = comment.content;
        previewUrl = (comment.image ?? '');
    });

    let errors = $state({} as Record<string, string[]>);
    let isSubmitting = $state(false);

    function handleImageSelect(event: Event) {
        const target = event.target as HTMLInputElement;
        const file = target.files?.[0];

        if (file) {
            formData.image = file;

            // Create preview
            const reader = new FileReader();
            reader.onload = (e) => {
                previewUrl = e.target?.result as string;
            };
            reader.readAsDataURL(file);

            // Clear any previous image errors
            delete errors.image;
            errors = { ...errors };
        }
    }

    // Real-time validation on single input field
    function handleInput<K extends keyof CommentInput>(field: K, value: CommentInput[K]) {
        // update the reactive $state object in-place instead of replacing it
        (formData as any)[field] = value;
        try {
            CommentSchema.pick({ [field]: true } as any).parse({ [field]: value } as any);
            const key = field as string;
            if (errors[key]) {
                delete errors[key];
                errors = { ...errors };
            }
        } catch (error) {
            if (error instanceof z.ZodError) {
                z.treeifyError(error);
            }
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
            const { image, ...commentData } = formData;
            CommentSchema.parse(commentData);

            // Create FormData for file upload
            const formDataToSend = new FormData();
            Object.entries(commentData).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    formDataToSend.append(key, value.toString());
                }
            });

            if (image) {
                formDataToSend.append('image', image);
            } else if (removeImage) {
                formDataToSend.append('removeImage', 'true');
            }

            const response = await fetch(`/api/posts/${formData.postId}/comments/${comment.id}/edit`, {
                method: 'POST',
                body: formDataToSend
            });

            if (response.ok) {
                showModal = false;
                previewUrl = '';
                // Refresh page to show new comment
                location.reload();
            } else {
                if (response.status === 409) {
                    errors = { ...errors, name: ['A comment with that name already exists.'] };
                    const element = document.getElementById('name') as HTMLInputElement | null;
                    element?.focus();
                    return;
                }
                alert('An error occurred while editing the comment. Please try again.');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('An unexpected error occurred. Please try again.');
        } finally {
            isSubmitting = false;
        }
    }

    function openModal() {
        showModal = true;
        formData = {
            postId: derivedPostId,
            parentId: derivedParentId,
            content: comment.content,
        };
        errors = {};
        previewUrl = '';
    }
</script>

<div>
    <button
        class="button-postcard edit clickable"
        onclick={openModal}
    >
        Edit
    </button>
</div>

<Modal bind:showModal>
	{#snippet header()}
		<h2>Edit Comment</h2>
	{/snippet}

    <form onsubmit={handleSubmit}>
		<!-- Content -->
        <div>
            <span title="The content of the comment.">ⓘ</span>
            <label for="content">Content:</label>
            <textarea
                id="content"
                bind:value={formData.content}
                oninput={(event) => handleInput('content', (event.target as HTMLTextAreaElement).value)}
                required
            ></textarea>
            {#if errors.content}
                <p class="error">{errors.content[0]}</p>
            {/if}
        </div>

		<!-- Image Upload -->
        <div>
            <label for="image">Image (optional):</label>
            <input
                type="file"
                id="image"
                class="small-input"
                accept="image/jpeg, image/png, image/gif, image/webp"
                onchange={handleImageSelect}
            />
            {#if previewUrl}
                <p class="preview-label">
                    {formData.image ? 'New image preview:' : 'Current image:'}
                </p>
                <img src={previewUrl} alt="Product preview" class="mw-100" />

                <!-- Option to remove current image -->
                {#if comment.image}
                    <button
                        type="button"
                        class="btn btn-md btn-secondary btn-codam mt-4"
                        onclick={() => { previewUrl = ''; removeImage = true; }}
                    >
                        Remove current image
                    </button>
                {/if}
            {/if}
            {#if errors.image}
                <p class="error">{errors.image[0]}</p>
            {/if}
        </div>

		<!-- Submit Button -->
        {#if isSubmitting}
            <button type="button" disabled>Submitting...</button>
        {:else}
            <button type="submit">Edit Comment</button>
        {/if}
    </form>
</Modal>
