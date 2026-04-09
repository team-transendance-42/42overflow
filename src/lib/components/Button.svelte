<script>
  export let label = "Button";
  export let type = "button";
  export let onClick = () => {};
</script>

<button {type} on:click={onClick}>
  {label}
</button>

<style>
  button {
    background-color: black;
    color: white;
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
	margin-bottom: 1rem;
  }

  button:hover {
    opacity: 0.85;
  }
</style>