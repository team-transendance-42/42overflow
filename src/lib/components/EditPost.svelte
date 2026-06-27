<script lang=ts>
    import { PostSchema } from '$lib/zodTypes.js';
    import type { PostInput } from '$lib/zodTypes.js';
    import { z } from 'zod';

    let showPopover = $state(false);

    interface Props {
        postId: number;
        post: any;
    }

    let { postId, post }: Props = $props();
    let derivedPostId = $derived(postId);
    let popover: HTMLDivElement;

    let formData = $state<PostInput>({
        postId: 0,
        title: '',
        content: '',
    });

    $effect(() => {
        formData.postId = derivedPostId;
        formData.title = post.title;
        formData.content = post.content;
    });

    let errors = $state({} as Record<string, string[]>);
    let isSubmitting = $state(false);

    // Real-time validation on single input field
    function handleInput<K extends keyof PostInput>(field: K, value: PostInput[K]) {
        // update the reactive $state object in-place instead of replacing it
        (formData as any)[field] = value;
        try {
            PostSchema.pick({ [field]: true } as any).parse({ [field]: value } as any);
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
            // Validate form data
            const { ...postData } = formData;
            PostSchema.parse(postData);

			const formDataToSend = new FormData();
            Object.entries(postData).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    formDataToSend.append(key, value.toString());
                }
            });

            const response = await fetch(`/api/posts/${formData.postId}/edit`, {
                method: 'POST',
                body: formDataToSend
            });

            if (response.ok) {
                showPopover = false;
                // Refresh page to show updated post
                location.reload();
            } else {
                alert('An error occurred while editing the post. Please try again.');
            }
        } catch (err) {
			if (err instanceof z.ZodError) {
				errors = z.flattenError(err).fieldErrors;
				return;
			}

			alert('An error occurred while editing the post. Please try again.');
			console.error('Unexpected error submitting:', err);
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
				<!-- Title -->
                <div class="textarea-group">
                    <label for="title">Title:</label>
                    <textarea
                        id="title"
                        bind:value={formData.title}
                        oninput={(event) => handleInput('title', (event.target as HTMLTextAreaElement).value)}
                        required
                    ></textarea>
                </div>
                {#if errors.title}
                    <p class="error">{errors.title[0]}</p>
                {/if}

                <!-- Content -->
                <div class="textarea-group">
                    <label for="content">Content:</label>
                    <textarea
                        id="content"
                        bind:value={formData.content}
                        oninput={(event) => handleInput('content', (event.target as HTMLTextAreaElement).value)}
                        required
                    ></textarea>
                </div>
                {#if errors.content}
                    <p class="error">{errors.content[0]}</p>
                {/if}

                <button
					class="button secondary"
					onclick={(event) => {
						event.stopPropagation();
						showPopover = false;
					}}
				>
                    Cancel
                </button>

                {#if isSubmitting}
                    <button type="button" class="button primary" disabled>
                        Submitting...
                    </button>
                {:else}
                    <button
						type="submit"
						class="button confirm"
					>
                        Confirm
                    </button>
                {/if}
            </form>
        </div>
    {/if}
</div>
