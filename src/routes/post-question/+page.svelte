<script>
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Tag from '$lib/components/Tag.svelte';

   let projectname = "";
   let topic = "";
   let body = "";
   let tagInput = "";
   let category = "memory";

   let tags = [];

function addTag() {
    if (!tagInput.trim()) return;

    tags = [
      ...tags,
      { text: tagInput.trim(), category }
    ];

    tagInput = "";
  }

  function removeTag(index) {
    tags = tags.filter((_, i) => i !== index);
  }
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


<div class="tag-input">
  <input
    placeholder="Add tag..."
    bind:value={tagInput}
  />

  <select bind:value={category}>
    <option value="memory">Memory</option>
    <option value="webserv">Webserv</option>
    <option value="custom">Custom</option>
  </select>

  <Button label="Add" type="add" />
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
    padding: 2rem;
    text-align: left;
  }
</style>