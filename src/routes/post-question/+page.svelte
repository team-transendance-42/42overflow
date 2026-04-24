<script>
  import { goto } from '$app/navigation';
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Tag from '$lib/components/Tag.svelte';

  let projectname = "";
  let body = "";
  let tagInput = "";
  let category = "memory";
  let tags = [];
  let error = "";

  async function submitQuestion() {
    if (!projectname || !body) {
      error = "Please fill in all fields.";
      return;
    }

    const res = await fetch('/api/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        projectname,
        body
      })
    });

    if (res.ok) {
      goto('/posts');
    } else if (res.status === 401) {
      error = "You must be logged in to post a question.";
    } else {
      error = "Something went wrong, please try again.";
    }
  }

  function addTag() {
    if (!tagInput.trim()) return;
    tags = [...tags, { text: tagInput.trim(), category }];
    tagInput = "";
  }

  function removeTag(index) {
    tags = tags.filter((_, i) => i !== index);
  }
</script>

<div class="post-question">
  <h1>ASK A QUESTION</h1>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  <Input
    label="Project Name"
    name="projectname"
    placeholder="Enter project name"
    bind:value={projectname}
  />

  <Textarea
    label="Question"
    name="body paragraph"
    placeholder="Write your question in detail here..."
    bind:value={body}
    rows={5}
  />

  <button on:click={submitQuestion}>Submit</button>

  <div class="tag-input">
    <input placeholder="Add tag..." bind:value={tagInput} />
    <select bind:value={category}>
      <option value="memory">Memory</option>
      <option value="webserv">Webserv</option>
      <option value="custom">Custom</option>
    </select>
    <button type="button" on:click={addTag}>Add</button>
  </div>

  <div class="tag-list">
    {#each tags as tag, i}
      <Tag
        text={tag.text}
        category={tag.category}
        removable={true}
        onRemove={() => removeTag(i)}
      />
    {/each}
  </div>
</div>

<style>
  .post-question {
    width: 100%;
    max-width: 700px;
    padding: 0rem;
    text-align: left;
  }
  .error {
    color: red;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
  }
</style>