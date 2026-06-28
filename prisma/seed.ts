import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const auth = betterAuth({
		database: prismaAdapter(prisma, { provider: 'postgresql' }),
		emailAndPassword: { enabled: true },
});

async function createUser(email: string, password: string, username: string, role: 'USER' | 'MODERATOR' | 'ADMIN') {
	try {
		const result = await auth.api.signUpEmail({
			body: {
				email: email,
				password: password,
				name: username,
			},
		});

		const user = await prisma.user.update({
			where: { id: result.user.id },
			data: {
				role: role,
				emailVerified: true,
			},
		});

		console.log(`✅ ${username} created successfully!\n`);

		return user;
	}
	catch (error) {
		const user = await prisma.user.findUnique({ where: { email } });
		if (user) {
			console.log(`⚠️ User with email ${email} already exists. Skipping creation.\n`);
			return user;
		} else {
			console.error(error);
			return null;
		}
	}
}

async function createSubject(subjectName: string, description: string, ownerId: string) {

	const slug = subjectName.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');

	try {
		const subject = await prisma.subject.create({
			data: {
				name: subjectName,
				slug: slug,
				description: description,
				memberships: {
					create: {
						userId: ownerId,
						role: 'OWNER',
					},
				},
			},
		});

		console.log(`✅ Subject "${subjectName}" created successfully!\n`);
		return subject;
	}
	catch (error) {
		
		const existingSubject = await prisma.subject.findUnique({ where: { slug } });
		
		if (existingSubject) {
			console.log(`⚠️ Subject "${subjectName}" already exists. Skipping creation.\n`);
			return existingSubject;
		} else {
			console.error(error);
		}
	}
}

async function createPost(title: string, content: string, subjectId: number, userId: string) {
	try {
		const post = await prisma.post.create({
			data: {
				title: title,
				content: content,
				subjectId: subjectId,
				userId: userId,
			},
		});
		console.log(`✅ Post "${title}" created successfully!\n`);
		return post;
	}
	catch (error) {
		console.error(error);
		return null;
	}
}

async function main()
{
	console.log('\nSeeding database ...\n');

	const user = await createUser('user@example.com', 'User123!', 'user', 'USER');
	const mod = await createUser('mod@example.com', 'Moderator123!', 'mod', 'MODERATOR');
	const admin = await createUser('admin@example.com', 'Admin123!', 'admin', 'ADMIN');

	// const libtft = await createSubject('Libft', 'This project is your very first project as a learner at 42. You will need to recode a few functions from the C standard library, as well as some other utility functions that you will use throughout your whole curriculum.', user?.id || '');
	// const pushSwap = await createSubject('Push Swap', 'This project is a simple sorting algorithm implementation.', mod?.id || '');
	// const getNextLine = await createSubject('Get Next Line', 'This project is about reading lines from a file.', admin?.id || '');

	// await createPost('Welcome to the Libft subject!', 'This is the first post in the Libft subject. Feel free to ask questions and share your progress.', libtft?.id || 0, user?.id || '');

	console.log('Database seeding completed!\n');
}

main()