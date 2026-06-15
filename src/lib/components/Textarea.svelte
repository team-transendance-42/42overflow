<script lang="ts">
  export let label = "";
  export let name = "";
  export let value = "";
  export let placeholder = "";
  export let rows = 4; 
  
</script>

<div class="textarea-group">
  {#if label}
    <label for={name}>{label}</label>
  {/if}

  <textarea
    class="black-text"
    bind:value
    id={name}
    name={name}
    placeholder={placeholder}
    rows={rows}
  >
  </textarea>

</div>
