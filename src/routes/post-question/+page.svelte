<script lang="ts">
  import Button from '$lib/components/Button.svelte';
</script>

<div class="post-question">
<h1>ASK A QUESTION</h1>

<p> This will have a field with inputs to post a question </p>


<Button label="Ask Question" type="submit" />
<Button label="Submit" type="submit" />

</div>

<style>
  .post-question {
    width: 100%;
    max-width: 800px;
    padding: 2rem;
    text-align: left;
  }
</style>