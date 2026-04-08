<script>
  import Input from '$lib/components/Input.svelte';
  import Button from '$lib/components/Button.svelte';
  import { enhance } from '$app/forms';

  export let form;
  let email = "", password = "";
</script>

<form method="POST" action="?/login" use:enhance>
  <div class="log-in-page">
    <h1>42Overflow</h1>
    {#if form?.error}
      <p class="error">{form.error}</p>
    {/if}
    <Input label="Email" name="email" placeholder="Enter email" bind:value={email} />
    <Input label="Password" name="password" placeholder="Enter password" bind:value={password} />
    <Button label="Log In" type="submit" />
    <p>Don't have an account? <a href="/signup"><strong>Sign up</strong></a></p>
  </div>
</form>

<style>
  .log-in-page { width: 100%; max-width: 400px; padding: 0; text-align: left; }
  .error { color: red; font-size: 0.875rem; }
</style>
