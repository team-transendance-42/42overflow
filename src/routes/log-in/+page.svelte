<script>
import Input from '$lib/components/Input.svelte';
import Button from '$lib/components/Button.svelte';

let name = "";
let email = "";
let password = "";

</script>


<div class="log-in-page">


<h1>LOG-IN</h1>

<Input
  label="Name"
  name="name"
  placeholder="Enter your name"
  bind:value={name}
/>


<Input
  label="Email"
  name="email"
  placeholder="Enter email here"
  bind:value={email}
/>

<Input
  label="Password"
  name="password"
  placeholder="Create Password"
  bind:value={password}
/>

<Button label="Create account" type="Create account" />

</div>



<style>
  .log-in-page {
    width: 100%;
    max-width: 400px;
    padding: 0rem;
    text-align: left;
  }
</style>

