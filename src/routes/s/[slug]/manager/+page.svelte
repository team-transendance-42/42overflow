<script lang="ts">
import SubjectMember from '$lib/components/SubjectMember.svelte';
import type { PageData } from './$types';
	let { data }: { data: PageData } = $props();
</script>

{#each data.members as member (member.userId)}
	<p>{member.user.name} </p>
{/each}