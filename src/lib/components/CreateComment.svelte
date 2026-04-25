<script lang=ts>
    import Modal from '$lib/components/Modal.svelte';
    import { CommentSchema } from '$lib/zodTypes.js';
    import type { CommentInput } from '$lib/zodTypes.js';
    import { z } from 'zod';

    let showModal = $state(false);

    interface Props {
        postId: number;
        parentId?: number;
    }

    let { postId, parentId }: Props = $props();
    let derivedPostId = $derived(postId);
    let derivedParentId = $derived(parentId ?? undefined);

    type CommentFormInput = CommentInput & {
        image?: File;
    };

    let formData = $state<CommentFormInput>({
        postId: 0,
        parentId: undefined,
        content: '',
    });

    $effect(() => {
        formData.postId = derivedPostId;
        formData.parentId = derivedParentId;
    });

    let errors = $state({} as Record<string, string[]>);
    let previewUrl = $state<string>('');
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
        formData = { ...formData, [field]: value } as CommentFormInput;
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
            }

            const response = await fetch(`/api/posts/${formData.postId}/comments/create`, {
                method: 'POST',
                body: formDataToSend
            });

            if (response.ok) {
                showModal = false;
                previewUrl = '';
                // Refresh page to show new product
                location.reload();
            } else {
                if (response.status === 409) {
                    errors = { ...errors, name: ['A product with that name already exists.'] };
                    const element = document.getElementById('name') as HTMLInputElement | null;
                    element?.focus();
                    return;
                }
                alert('An error occurred while creating the product. Please try again.');
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
            content: '',
        };
        errors = {};
        previewUrl = '';
    }

</script>

<div>
    <button onclick={openModal}>
        {#if derivedParentId}
            Reply
        {/if}
        {#if !derivedParentId}
            Create New Comment
        {/if}
    </button>
</div>

<Modal bind:showModal>
	{#snippet header()}
		<h2>Create New Comment</h2>
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
                <div>
                    <img src={previewUrl} alt="Preview" class="w-100"/>
                </div>
            {/if}
            {#if errors.image}
                <p class="error">{errors.image[0]}</p>
            {/if}
        </div>

		<!-- Submit Button -->
        {#if isSubmitting}
            <button type="button" disabled>Submitting...</button>
        {:else}
            <button type="submit">Create Comment</button>
        {/if}
    </form>
</Modal>
