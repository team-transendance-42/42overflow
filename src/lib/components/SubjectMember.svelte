<script lang="ts">
	import Avatar from '$lib/components/Avatar.svelte';

	type MemberRole = 'MEMBER' | 'CURATOR' | 'OWNER';

	type SubjectMemberProps = {
		member: {
			userId: string;
			role: MemberRole;
			joined_at: string | Date;
			user: {
				id: string;
				name: string;
				image: string | null;
			};
		};
		onUpdate: (userId: string, role: MemberRole) => void | Promise<void>;
		isSaving?: boolean;
	};

	let {
		member,
		onUpdate,
		isSaving = false
	}: SubjectMemberProps = $props();

	let selectedRole = $state<MemberRole>('MEMBER');

	$effect(() => {
		selectedRole = member.role;
	});

	const joinedAt = $derived(new Date(member.joined_at).toLocaleDateString());
	const hasChanges = $derived(selectedRole !== member.role);

	function handleUpdate() {
		onUpdate(member.userId, selectedRole);
	}
</script>

<article class="user-card">
	<div class="user-main">
		<Avatar src={member.user.image ?? ''} size="42px" alt={member.user.name} />
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
		<button onclick={handleUpdate}>
			update
		</button>
	</div>
</article>

<style>
	.user-card {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
		padding: 0.9rem;
		border: 1px solid var(--color-neutral-400);
		border-radius: var(--radius-md);
		background-color: var(--color-neutral-100);
	}

	.user-main {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		min-width: 0;
	}

	.user-text {
		min-width: 0;
	}

	.user-text h2 {
		margin: 0;
		font-size: 1rem;
	}

	.joined-row {
		margin: 0.2rem 0 0;
		font-size: 0.9rem;
		display: flex;
		gap: 0.3rem;
	}

	.joined-label {
		font-weight: 600;
 	}

	.joined-value {
		min-width: 12ch;
	}

	.user-meta {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 0.3rem;
		font-size: 0.85rem;
 	}

	.role {
		display: inline-block;
		padding: 0.1rem 0.5rem;
		font-weight: 700;
	}

	.role-member {
		color: var(--color-neutral-500);
	}

	.role-curator {
		color: #28408f;
	}

	.role-owner {
		color: #8f440f;
	}

	.action-link {
		padding: 0;
		border: none;
		background: transparent;
		font-weight: 600;
		cursor: pointer;
		text-decoration: underline;
		font-size: 0.85rem;
	}

	.action-link:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		text-decoration: none;
	}

	@media (max-width: 640px) {
		.user-card {
			flex-direction: column;
			align-items: flex-start;
		}

		.user-meta {
			align-items: flex-start;
		}
	}
</style>
