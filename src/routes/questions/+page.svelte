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
    <h2><strong>Project Name:</strong> {q.title}</h2>
    <p class="content"><strong>Question: </strong> {q.content}</p>

    {#if q.profile?.user?.name}
      <p class="author">Posted by: 

	  	<a 
			class="author-link"
			href="/profile/{q.profile.username}"
		>
	  		{q.profile.user.name}
	  	</a>
	 </p>
    {/if}
  </Postbox>
{/each}


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
    margin: 0 auto;   
  
  }

.content {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.author-link {
  font-style: italic;
  color: #083957;
  text-decoration: none;
}
.author-link:hover {
  text-decoration: underline;
}

</style>