<script lang="ts">
  export let label = "";
  export let placeholder = "";
  export let value = "";
  export let name = "";
  export let rows = 4; // default height
</script>

<div class="textarea-group">
  {#if label}
    <label for={name}>{label}</label>
  {/if}

  <textarea
    bind:value
    id={name}
    name={name}
    placeholder={placeholder}
    rows={rows}
  >
  </textarea>

</div>

<style>
.textarea-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 0.4rem;
}

label {
  font-size: 0.9rem;
  font-weight: 500;
}

textarea {
  padding: 0.7rem 0.9rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
  outline: none;
  transition: border 0.2s ease;

  resize: vertical; /* user can resize vertically */
}

textarea:focus {
  border-color: black;
}
</style>