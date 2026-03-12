<script lang="ts">
  import { onMount } from 'svelte';
  import Postbox from '$lib/components/Postbox.svelte';

let questions = [];

onMount(async () => {
    const res = await fetch('/api/questions');
    questions = await res.json();
  });

</script>

<div class="questions-page">
<h1>QUESTIONS</h1>

{#each questions as q}

    <Postbox>
	 <h2>{q.projectname}</h2>
      <h2>{q.topic}</h2>
      <p>{q.body}</p>
    </Postbox>
  {/each}


<p> This will have a list of questions/posts from students etc </p>

</div>



<style>
  .questions-page {
    width: 100%;
    max-width: 3400px;
    margin: 0 auto;   /* THIS centers it */
  
  }
</style>