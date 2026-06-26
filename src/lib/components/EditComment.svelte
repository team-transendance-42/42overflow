<script lang=ts>
    import { CommentSchema } from '$lib/zodTypes.js';
    import type { CommentInput } from '$lib/zodTypes.js';
    import { z } from 'zod';

    let showPopover = $state(false);

    interface Props {
        postId: number;
        parentId?: number;
        comment: any;
    }

    let { postId, parentId, comment }: Props = $props();
    let derivedPostId = $derived(postId);
    let derivedParentId = $derived(parentId ?? undefined);
    let removeImage = $state(false);
    let popover: HTMLDivElement;

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

    function removeOldImage() {
		previewUrl = '';
		formData.image = undefined;
		removeImage = true;
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
                showPopover = false;
                previewUrl = '';
                // Refresh page to show updated comment
                location.reload();
            } else {
                alert('An error occurred while editing the comment. Please try again.');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('An unexpected error occurred. Please try again.');
        } finally {
            isSubmitting = false;
        }
    }

    function handleDocumentClick(event: PointerEvent) {
        if (
            showPopover &&
            popover &&
            !popover.contains(event.target as Node)
        ) {
            showPopover = false;
        }
    }
</script>

<svelte:document onpointerdown={handleDocumentClick} />

<div class="comment-container black-text">
    <div>
        <button
            class="button postcard edit clickable"
            onclick={(e) => {
                e.stopPropagation();
                showPopover = !showPopover
            }}
        >
            Edit
        </button>
    </div>

    {#if showPopover}
        <div
            class="comment-popover"
            bind:this={popover}
        >
            <form onsubmit={handleSubmit}>
                <!-- Content -->
                <div class="textarea-group">
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
                <div class="input-group">
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
                    {#if previewUrl}
                        <button type="button" class="button unsubscribe" onclick={removeOldImage}>
                            <strong>Remove Image</strong>
                        </button>
                    {/if}
                </div>

                <button class="button secondary" onclick={() => showPopover = false}>
                    Cancel
                </button>

                {#if isSubmitting}
                    <button type="button" class="button secondary" disabled>
                        Submitting...
                    </button>
                {:else}
                    <button type="submit" class="button confirm">
                        Confirm
                    </button>
                {/if}
            </form>
        </div>
    {/if}
</div>
