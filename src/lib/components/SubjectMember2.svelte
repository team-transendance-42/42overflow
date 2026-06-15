<script lang="ts">

	// type Member = {
	// 	userId: string;
	// 	role: 'MEMBER' | 'CURATOR' | 'OWNER';
	// 	joined_at: string | Date;
	// 	user: {
	// 		id: string;
	// 		name: string;
	// 		image: string | null;
	// 	};
	// };

	let { member } = $props();

	const joinedAt = new Date(member.joined_at).toLocaleDateString();
	let selectedRole = $derived(member.role);

	async function updateRole() {
		// console.log(`Update ${member.user.name} to role ${selectedRole}`);
		// const res = await fetch(`/api/subjects//members`, )
	}
</script>

<article class="user-card">
	<div class="user-main">
		<!-- <Avatar src={member.user.image ?? ''} size="42px" alt={member.user.name} /> -->
		<div class="user-text">
			<h2>{member.user.name}</h2>
			<p class="joined-row">
				<span class="joined-label">Joined:</span>
				<span class="joined-value">{joinedAt}</span>
			</p>
		</div>
	</div>

	<div class="user-meta">
		<select name="role" bind:value={selectedRole}>
			<option value="MEMBER">MEMBER</option>
			<option value="CURATOR">CURATOR</option>
			<option value="OWNER">OWNER</option>
		</select>
		<button onclick={updateRole}>
			update
		</button>
	</div>
</article>