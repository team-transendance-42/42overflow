<script lang="ts">
  export let label = "Button";
  export const variant: "button" | "submit" | "reset" = "button";
  export let onClick = () => {};
</script>

<button type={variant} on:click={onClick}>
  {label}
</button>

<style>
  button {
    background-color: var(--color-neutral-900);
    color: var(--color-neutral-200);
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