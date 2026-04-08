<script lang="ts">
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import Avatar from '$lib/components/Avatar.svelte';
  import { enhance } from '$app/forms';

  export let data;
  export let form;

  let firstname = data.user?.name?.split(' ')[0] ?? '';
  let lastname = data.user?.name?.split(' ')[1] ?? '';
  let email = data.user?.email ?? '';
  let intraprofile = '';
  let campus = '';

  let previewUrl = data.user?.image ?? '';

  function handleFileChange(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) previewUrl = URL.createObjectURL(file);
  }
</script>

<form method="POST" action="?/update" use:enhance enctype="multipart/form-data">
  <div class="profile-page">
    <h1>PROFILE</h1>

    {#if form?.error}
      <p class="error">{form.error}</p>
    {/if}
    {#if form?.success}
      <p class="success">Profile updated!</p>
    {/if}

    <div class="avatar-wrapper">
  		<Avatar src={previewUrl} size="80px" />
  
  		<label class="upload-btn">
    		<strong>Upload photo</strong>
    		<input
      			type="file"
      			name="avatarimage"
      			accept="image/*"
      			on:change={handleFileChange}
    		/>
  		</label>



    </div>

    <div class="name-row">
      <Input label="First Name" name="firstname" placeholder="First" bind:value={firstname} />
      <Input label="Last Name" name="lastname" placeholder="Last" bind:value={lastname} />
    </div>

    <Input label="E-mail" name="email" placeholder="E-mail" bind:value={email} />
    <Input label="Campus" name="campus" placeholder="Campus" bind:value={campus} />
    <Input label="Intra Profile" name="intraprofile" placeholder="Intra profile" bind:value={intraprofile} />

    <Button label="Update" type="submit" />
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
  padding: 6px 14px;
  border: 0.5px solid var(--color-border-secondary);
  border-radius: var(--border-radius-md);
  display: inline-block;
}

.upload-btn input {
  display: none;
}

.file-hint {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

</style>