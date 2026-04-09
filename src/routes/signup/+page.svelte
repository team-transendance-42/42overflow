<script lang="ts">
  import Input from '$lib/components/Input.svelte';
  import Button from '$lib/components/Button.svelte';
  import { authClient } from '$lib/auth-client';
  import { goto } from '$app/navigation';

  let email = '';
  let password = '';
  let name = '';
  let error = '';
  let loading = false;

  async function handleSignup() {
    error = '';
    loading = true;

    const { data, error: err } = await authClient.signUp.email({
      email,
      password,
      name,
    });

    loading = false;

    if (err) {
      error = err.message ?? 'Could not create account';
      return;
    }

    goto('/profile');
  }
</script>

<div class="sign-up-page">
  <h1>42Overflow</h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <Input label="Name" name="name" placeholder="Your name" bind:value={name} />
  <Input label="Email" name="email" placeholder="Enter email" bind:value={email} />
  <Input label="Password" name="password" placeholder="Enter password" bind:value={password} />

  <Button label={loading ? 'Creating account...' : 'Sign Up'} type="button" onClick={handleSignup} />

  <p>Already have an account? <a href="/login">Log in</a></p>
</div>

<style>
  .sign-up-page { width: 100%; max-width: 400px; padding: 0; text-align: left; }
  .error { color: red; font-size: 0.875rem; }
</style>


