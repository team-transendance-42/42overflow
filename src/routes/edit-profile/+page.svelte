<script lang="ts">
	import Avatar from '$lib/components/Avatar.svelte';
	import { type EditProfileInput } from '$lib/zodTypes';
	import { EditProfileSchema } from '$lib/zodTypes';
	import { z } from 'zod';

	interface Props {
		data: {
			user: EditProfileInput & {
				email?: string;
				image?: string;
			};
		};
	}
	let { data }: Props = $props();

	let derivedUserid = $derived(data.user?.id ?? '');
	let derivedFirstname = $derived(data.user?.first_name ?? '');
	let derivedLastname = $derived(data.user?.last_name ?? '');
	let derivedEmail = $derived(data.user?.email ?? '');
	let derivedInterests = $derived(data.user?.interests ?? '');
	let derivedUsername = $derived(data.user?.name ?? '');

	let success = $state(false);
	let removeImage = $state(false);

	// Add a reference to the file input for avatar upload
	type EditProfileWithImageInput = EditProfileInput & {
		image?: File;
	};

	let formData = $state<EditProfileWithImageInput>({
		id: '',
		name: '',
		first_name: '',
		last_name: '',
		interests: '',
		image: undefined
	});

	let previewUrl = $state<string>('');

	$effect(() => {
		formData.id = derivedUserid;
        formData.name = derivedUsername;
		formData.first_name = derivedFirstname;
		formData.last_name = derivedLastname;
		formData.interests = derivedInterests;
		previewUrl = (data.user.image ?? '');
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
    function handleInput<K extends keyof EditProfileWithImageInput>(field: K, value: EditProfileWithImageInput[K]) {
        // update the reactive $state object in-place instead of replacing it
        (formData as any)[field] = value;
        try {
            EditProfileSchema.pick({ [field]: true } as any).parse({ [field]: value } as any);
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
            const { image, ...profileData } = formData;
            EditProfileSchema.parse(profileData);

            // Create FormData for file upload
            const formDataToSend = new FormData();
            Object.entries(profileData).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    formDataToSend.append(key, value.toString());
                }
            });

            if (image) {
                formDataToSend.append('image', image);
            } else if (removeImage) {
                formDataToSend.append('removeImage', 'true');
            }

            const response = await fetch(`?/update`, {
                method: 'POST',
                body: formDataToSend
            });

            if (response.ok) {
                previewUrl = '';
                // Refresh page to show updated profile
                location.reload();
            } else {
                alert('An error occurred while editing the profile. Please try again.');
            }
        } catch (err) {
			if (err instanceof z.ZodError) {
				errors = z.flattenError(err).fieldErrors;
				return;
			}

            alert('An error occurred while editing the profile. Please try again.');
			console.error('Unexpected error submitting:', err);
		} finally {
			isSubmitting = false;
		}
    }
</script>

<form onsubmit={handleSubmit}>
	<div class="profile-page">
		<h1><strong>PROFILE PAGE</strong></h1>

		{#if success}
			<p class="success">Profile updated!</p>
		{/if}

		<div class="avatar-wrapper">
			<Avatar src={previewUrl}/>
			<label class="upload-btn">
				<strong>Upload avatar</strong>
				<input
					type="file"
					id="image"
					class="small-input"
					accept="image/jpeg, image/png, image/gif, image/webp"
					onchange={handleImageSelect}
				/>
			</label>
			{#if previewUrl}
				<button type="button" class="button unsubscribe" onclick={removeOldImage}>
					<strong>Remove avatar</strong>
				</button>
			{/if}
		</div>

		<!-- First & Last Name -->
		<div class="name-row">
			<input
				class="input-group"
				placeholder="First"
				id="firstname"
				bind:value={formData.first_name}
                oninput={(event) => handleInput('first_name', (event.target as HTMLTextAreaElement).value)}
			/>
			<input
				class="input-group"
				placeholder="Last"
				id="lastname"
				bind:value={formData.last_name}
                oninput={(event) => handleInput('last_name', (event.target as HTMLTextAreaElement).value)}
			/>
		</div>
		{#if errors.first_name}
			<p class="error">{errors.first_name[0]}</p>
		{/if}
		{#if errors.last_name}
			<p class="error">{errors.last_name[0]}</p>
		{/if}

		<!-- User Name -->
		<input
			class="input-group"
			placeholder="User name"
			id="username"
			bind:value={formData.name}
            oninput={(event) => handleInput('name', (event.target as HTMLTextAreaElement).value)}
		/>
		{#if errors.name}
			<p class="error">{errors.name[0]}</p>
		{/if}
		<!-- E-mail -->
		<input
			class="input-group"
			placeholder="E-mail"
			id="email"
			bind:value={derivedEmail}
			disabled
		/>
		<!-- Interests -->
		<input
			class="input-group"
			placeholder="Interests"
			id="interests"
			bind:value={formData.interests}
            oninput={(event) => handleInput('interests', (event.target as HTMLTextAreaElement).value)}
		/>
		{#if errors.interests}
			<p class="error">{errors.interests[0]}</p>
		{/if}

		{#if isSubmitting}
			<button type="button" class="button secondary" disabled>
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
	.avatar-wrapper { margin: 0.5rem 0; display: flex; flex-direction: column; gap: 0.5rem; }
	.profile-page { width: 100%; max-width: 490px; padding: 0; text-align: left; }
	.name-row { display: flex; gap: 1rem; }
	.name-row :global(.input-wrapper) { flex: 1; }
	.success { color: green; font-size: 0.875rem; }

	.upload-btn {
	cursor: pointer;
	font-size: 0.875rem;
	border: 0.5px solid var(--color-border-secondary);
	border-radius: var(--border-radius-md);
	display: inline-block;
}

.upload-btn input {
	display: none;
}

</style>