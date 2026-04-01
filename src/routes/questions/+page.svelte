<script lang="ts">
  import { onMount } from 'svelte';
  import Postbox from '$lib/components/Postbox.svelte';

let questions = [];
  let page = 1;
  let limit = 10;
  let total = 0;

async function loadQuestions() {
    const res = await fetch(`/api/questions?page=${page}&limit=${limit}`);
    const json = await res.json();

	questions = json.data;  
    total = json.total;
  };

  onMount(loadQuestions);
</script>

<div class="questions-page">
<h1>QUESTIONS</h1>

{#each questions as q}

    <Postbox>
	 <h2>Project name: {q.projectname}</h2>
      <h2>Topic: {q.topic}</h2>
      <p>Summary: {q.body}</p>
    </Postbox>
  {/each}


<p> This will have a list of questions/posts from students etc </p>

</div>

<div class="pagination">
  <button on:click={() => {
    if (page > 1) {
      page--;
      loadQuestions();
    }
  }}>
    Prev 
  </button>

  <span> - Page {page} -</span>

  <button on:click={() => {
    if (page * limit < total) {
      page++;
      loadQuestions();
    }
  }}>
    Next
  </button>
</div>



<style>
  .questions-page {
    width: 100%;
    max-width: 3400px;
    margin: 0 auto;   /* THIS centers it */
  
  }
</style>