<script>
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';

   let projectname = "";
   let topic = "";
   let body = "";

</script>

<div class="post-question">
<h1>ASK A QUESTION</h1>


<Input
  label="Project Name"
  name="projectname"
  placeholder="Enter project name"
  bind:value={projectname}
/>

<Input
  label="Topic"
  name="topic"
  placeholder="Enter your topic"
  bind:value={topic}
/>

<Textarea
  label="Body"
  name="body paragraph"
  placeholder="Write your question in detail here..."
  bind:value={body}
  rows={5}
/>

<p>You typed: {projectname}</p>

<Button label="Submit" type="submit" />


</div>

<style>
  .post-question {
    width: 100%;
    max-width: 700px;
    padding: 2rem;
    text-align: left;
  }
</style>