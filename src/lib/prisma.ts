import { PrismaClient } from '@prisma/client';
import { dev } from '$app/environment';

declare global {
	// eslint-disable-next-line no-var
    var __prisma: PrismaClient | undefined;
}

// Configure amount of logging based on environment
const prismaOptions = dev
	? {
		log: [
			{ emit: 'stdout' as const, level: 'query' as const },
			{ emit: 'stdout' as const, level: 'error' as const },
			{ emit: 'stdout' as const, level: 'warn' as const }
		],
	}
	: {
		log: [{ emit: 'stdout' as const, level: 'error' as const }],
    };

let prisma: PrismaClient;

if (dev) {
    // In development, use global to avoid recreating connections
    if (!globalThis.__prisma) {
        globalThis.__prisma = new PrismaClient(prismaOptions);
    }
    prisma = globalThis.__prisma;
} else {
    // In production, create a new instance
    prisma = new PrismaClient(prismaOptions);
}

// Ensure the client connects
prisma.$connect().catch((e) => {
	console.error('Prisma connect error', e);
});

// Graceful shutdown
if (typeof process !== 'undefined' && process && !dev) {
	// in production detach on termination signals
	const shutdown = async () => {
		try {
			await prisma.$disconnect();
		} catch (e) {
			console.error('Error disconnecting Prisma: ', e);
		} finally {
			process.exit(0);
		}
	};

	// Shut down gracefully on termination signals (CTRL+C, CTRL+D)
	process.on('SIGINT', shutdown);
	process.on('SIGTERM', shutdown);
} else if (dev) {
	// in dev, still try to clean up on HMR-reloads/stop
	const shutdown = async () => {
		try {
			await prisma.$disconnect();
		} catch {
			/* ignore */
		}
	};

	// Shut down gracefully on termination signals (CTRL+C, CTRL+D)
	process.on('SIGINT', shutdown);
	process.on('SIGTERM', shutdown);
}

export default prisma;
