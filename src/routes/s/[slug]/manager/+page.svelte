<script lang="ts">
	import SubjectMember2 from '$lib/components/SubjectMember2.svelte';
	import type { PageData } from './$types';
	
	type MemberRole = 'MEMBER' | 'CURATOR' | 'OWNER';
	
	let { data }: { data: PageData } = $props();
	
	// let savingUserId = $state<string | null>(null);
	
	// async function updateMemberRole(targetUserId: string, role: MemberRole) {
	// 	try {
	// 		const res = await fetch(`/api/subjects/${}/members`, {
	// 			method: 'PATCH',
	// 			headers: { 'content-type': 'application/json' },
	// 			body: JSON.stringify({ targetUserId, role })
	// 		});
	// 		if (!res.ok) throw new Error('Failed');
	// 		// optionally refresh data
	// 	} finally {
	// 		savingUserId = null;
	// }
	// }

</script>

{#each data.members as member (member.userId)}
	<SubjectMember2 {member} />
{/each}
