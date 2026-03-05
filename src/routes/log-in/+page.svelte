<script>
import Input from '$lib/components/Input.svelte';
import Button from '$lib/components/Button.svelte';

let email = "";
let password = "";

</script>


<div class="log-in-page">


<h1>42Overflow </h1>

<Input
  label="Email"
  name="email"
  placeholder="Enter email"
  bind:value={email}
/>


<Input
  label="Password"
  name="password"
  placeholder="Enter password"
  bind:value={password}
/>

<Button label="Log In" type="Log in" />


<p>Don’t have an account? Sign up </p>

</div>



<style>
  .log-in-page {
    width: 100%;
    max-width: 400px;
    padding: 0rem;
    text-align: left;
  }
</style>

