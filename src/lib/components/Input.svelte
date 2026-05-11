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
    bind:value
    type={type}
    name={name}
    id={name}
    placeholder={placeholder}
	{disabled}
  />
</div>

<style>

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: .4rem;

  }
  
  input {
    border: 1px solid #ccc;
    border-radius: 6px;
    outline: none;
    transition: border 0.2s ease;
  }

  label {
    font-size: 0.9rem;
    font-weight: 500;
  }

  input {
    padding: 0.7rem 0.9rem;
    border-radius: 6px;
    border: 1px solid #ccc;
    font-size: 1rem;
    outline: none;
    transition: border 0.2s ease;
  }

  input:focus {
    border-color: black;
  }

  input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>