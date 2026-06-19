<script lang="ts">
	import SubjectMember from '$lib/components/SubjectMember.svelte';
	import type { PageData } from './$types';

	type MemberRole = 'MEMBER' | 'CURATOR' | 'OWNER';
	type Member = {
		userId: string;
		role: MemberRole;
		joined_at: string | Date;
		user: {
			id: string;
			name: string;
			image: string | null;
		};
	};

	let { data }: { data: PageData } = $props();

	import { onMount } from 'svelte';

	let roleOverrides = $state<Record<string, MemberRole>>({});
	let savingUserId = $state<string | null>(null);
	let isArchiving = $state(false);
	let message = $state('');
	let errorMessage = $state('');

	let fetchedMembers = $state<any[]>([]);

	const members = $derived(
		fetchedMembers.map((member) => ({
			...member,
			role: roleOverrides[member.userId] ?? member.role
		}))
	);

	const ownerCount = $derived(members.filter((member) => member.role === 'OWNER').length);

	async function updateMemberRole(targetUserId: string, role: MemberRole) {
		savingUserId = targetUserId;
		message = '';
		errorMessage = '';

		try {
			const res = await fetch(`/api/subjects/${data.subject.slug}/members`, {
				method: 'PATCH',
				headers: {
					'content-type': 'application/json'
				},
				body: JSON.stringify({
					targetUserId,
					role
				})
			});

			if (!res.ok) {
				errorMessage = `Failed to update role (${res.status})`;
				return;
			}

			const json = await res.json();
			const updatedMember = json.data;

			fetchedMembers = fetchedMembers.map((member) =>
				member.userId === updatedMember.userId ? updatedMember : member
			);

			message = 'Role updated successfully.';
		} catch (err) {
			errorMessage = 'Failed to update role';
		} finally {
			savingUserId = null;
		}
	}

	async function archiveSubject() {
		message = '';
		errorMessage = '';

		const isConfirmed = window.confirm(
			`Are you sure you want to archive "${data.subject.name}"? This action cannot be undone.`
		);

		if (!isConfirmed) {
			return;
		}

		isArchiving = true;

		try {
			const res = await fetch('/api/subjects/archive', {
				method: 'POST',
				headers: {
					'content-type': 'application/json'
				},
				body: JSON.stringify({ slug: data.subject.slug })
			});

			if (!res.ok) {
				const text = await res.text();
				errorMessage = text || `Failed to archive subject (${res.status})`;
				return;
			}

			message = 'Subject archived successfully.';
		} catch (err) {
			errorMessage = 'Failed to archive subject';
		} finally {
			isArchiving = false;
		}
	}

	onMount(async () => {
		try {
			const res = await fetch(`/api/subjects/${data.subject.slug}/members`);
			if (!res.ok) {
				errorMessage = `Failed to load members (${res.status})`;
				return;
			}

			const json = await res.json();
			fetchedMembers = json.data ?? [];
		} catch (err) {
			errorMessage = 'Failed to load members';
		}
	});
</script>

<section class="manage-page">
	<!-- <header class="manage-header">
		<p class="eyebrow">Owner controls</p>
		<h1>Manage {data.subject.name}</h1>
		<p class="subhead">Promote members to curator or demote curators back to member.</p>
		<p class="meta">Owners in this subject: {ownerCount}</p>
	</header> -->

	{#if message}
		<p class="message success">{message}</p>
	{/if}

	{#if errorMessage}
		<p class="message error">{errorMessage}</p>
	{/if}

	<div class="member-list">
		{#each members as member (member.userId)}
			<SubjectMember
				{member}
				onUpdate={updateMemberRole}
				isSaving={savingUserId === member.userId}
			/>
		{/each}
	</div>

	<div>
		<a href="/s/{data.subject.slug}/edit">Edit description</a>
	</div>
	<div>
		<button on:click={archiveSubject} disabled={isArchiving}>
			{isArchiving ? 'Archiving…' : 'Archive Subject'}
		</button>
	</div>
</section>

<style>
	.manage-page {
		max-width: 860px;
		margin: 0 auto;
		padding: 1.5rem 1rem 2rem;
	}

	.manage-header h1 {
		margin: 0;
		font-size: 1.7rem;
	}

	.eyebrow {
		margin: 0 0 0.2rem;
		text-transform: uppercase;
		font-size: 0.75rem;
		letter-spacing: 0.08em;
		color: var(--color-neutral-500);
	}

	.subhead {
		margin: 0.5rem 0 0;
		color: var(--color-neutral-500);
	}

	.meta {
		margin-top: 0.65rem;
		font-size: 0.88rem;
		color: var(--color-neutral-500);
	}

	.member-list {
		display: grid;
		gap: 0.75rem;
		margin-top: 1rem;
	}

	.message {
		padding: 0.7rem 0.9rem;
		border-radius: 8px;
		margin-top: 1rem;
		font-size: 0.95rem;
	}

	.success {
		background: #e6f8ea;
		color: #0a5a26;
	}

	.error {
		background: #fde9e9;
		color: #7d1111;
	}
</style>
