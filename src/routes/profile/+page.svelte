<script>
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import Avatar from '$lib/components/Avatar.svelte';
  
  let avatarimage = "";
  let firstname = "";
  let lastname = "";
  let email = "";
  let password = "";
  let campus = "";
  let intraprofile = "";

</script>

<div class="profile-page">
  <h1>PROFILE</h1>


<div class="avatar-wrapper">
  <Avatar />
</div>

<div class="name-row">
  <Input
    label="First Name"
    name="firstname"
    placeholder="First"
    bind:value={firstname} />
  <Input
    label="Last Name"
    name="lastname"
    placeholder="Last"
    bind:value={lastname} />
</div>

<Input
  label="E-mail"
  name="email"
  placeholder="E-mail"
  bind:value={email}
/>

<Input
  label="Password"
  name="password"
  placeholder="Password"
  bind:value={password}
/>

<Input
  label="Image"
  name="avatarimage"
  placeholder="Link for profile picture"
  bind:value={avatarimage}
/>

<Input
  label="Campus"
  name="campus"
  placeholder="Campus"
  bind:value={campus}
/>

<Input
  label="Intra Profile"
  name="intraprofile"
  placeholder="Intra profile"
  bind:value={intraprofile}
/>

<Button label="Update" type="update" />

</div>


<style>

.avatar-wrapper {
  margin-top: .5rem;
  margin-bottom: .5rem;
}
  .profile-page {
    width: 100%;
    max-width: 490px;
    padding: 0rem;
    text-align: left;

  }

  .name-row {
  display: flex;
  gap: 1rem;
}

.name-row :global(.input-wrapper) {
  flex: 1; /* each takes equal half of the row */
}
</style>