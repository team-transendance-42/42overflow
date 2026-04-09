<script lang="ts">
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import Avatar from '$lib/components/Avatar.svelte';
  import { authClient } from '$lib/auth-client';

  export let data;

  let firstname = data.user?.name?.split(' ')[0] ?? '';
  let lastname = data.user?.name?.split(' ')[1] ?? '';
  let email = data.user?.email ?? '';
  let interests = data.user?.interests ?? '';
  let intraprofile = data.profile?.login ?? '';
  let campus = data.profile?.campus ?? '';
  let previewUrl = data.user?.image ?? '';
  let error = '';
  let success = false;
  let loading = false;

  let fileInput: HTMLInputElement;

  function handleFileChange(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) previewUrl = URL.createObjectURL(file);
  }

  function removeAvatar() {
  previewUrl = '';
  if (fileInput) fileInput.value = ''; // reset the input
}

  async function handleUpdate() {
    error = '';
    success = false;
    loading = true;

    const { error: err } = await authClient.updateUser({
      name: `${firstname} ${lastname}`.trim(),
      image: previewUrl || '',
    });

    loading = false;

    if (err) {
      error = err.message ?? 'Could not update profile';
      return;
    }

    success = true;
  }
</script>

<form method="POST" action="?/update" use:enhance enctype="multipart/form-data">
<div class="profile-page">
  <h1><strong>PROFILE PAGE</strong></h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}
  {#if success}
    <p class="success">Profile updated!</p>
  {/if}

  <div class="avatar-wrapper">
    <Avatar src={previewUrl} size="80px" />
    <label class="upload-btn">
      <strong>Upload avatar</strong>
      <input type="file" name="avatarimage" accept="image/*" bind:this={fileInput} on:change={handleFileChange} />
    </label>
    {#if previewUrl}
      <button type="button" class="remove-btn" on:click={removeAvatar}>
        <strong>Remove avatar</strong>
      </button>
    {/if}
  </div>

  <div class="name-row">
    <Input label="First Name" name="firstname" placeholder="First" bind:value={firstname} />
    <Input label="Last Name" name="lastname" placeholder="Last" bind:value={lastname} />
  </div>

  <Input label="E-mail" name="email" placeholder="E-mail" bind:value={email} />
  <Input label="Interests" name="interests" placeholder="Interests" bind:value={interests} />
  <Input label="Campus" name="campus" placeholder="Campus" bind:value={campus} />
  <Input label="Intra Profile" name="intraprofile" placeholder="Intra profile" bind:value={intraprofile} />

  <Button label={loading ? 'Saving...' : 'Update'} type="button" onClick={handleUpdate} />
</div>
</form>

<style>
  .avatar-wrapper { margin: 0.5rem 0; display: flex; flex-direction: column; gap: 0.5rem; }
  .profile-page { width: 100%; max-width: 490px; padding: 0; text-align: left; }
  .name-row { display: flex; gap: 1rem; }
  .name-row :global(.input-wrapper) { flex: 1; }
  .error { color: red; font-size: 0.875rem; }
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

.remove-btn  {
  cursor: pointer;
  font-size: 0.875rem;
  border: 0.5px solid var(--color-border-secondary);
  border-radius: var(--border-radius-md);
  display: flex;
}

.remove-btn input {
  display: none;
}

.file-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

</style>