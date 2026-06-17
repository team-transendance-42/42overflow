<script lang=ts>
  export let label = "";
  export let type = "text";
  export let placeholder = "";
  export let value = "";
  export let name = "";
  export let disabled = false;
</script>

<div class="input-group">
  {#if label}
    <label for={name}>{label}</label>
  {/if}

  <input
    class="black-text"
    bind:value
    type={type}
    name={name}
    id={name}
    placeholder={placeholder}
	{disabled}
  />
</div>
