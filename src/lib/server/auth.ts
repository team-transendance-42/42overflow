import { betterAuth } from 'better-auth';
import { prismaAdapter } from 'better-auth/adapters/prisma';
import { db } from '$lib/server/db';

export const auth = betterAuth({
  database: prismaAdapter(db, {
    provider: 'postgresql',
  }),
  user: {
	additionalFields: {
    	first_name: { type: "string", required: false, fieldName: "first_name" },
    	last_name: { type: "string", required: false, fieldName: "last_name" },
		biography: { type: "string", required: false, fieldName: "biography" },
		interests: { type: "string", required: false, fieldName: "interests" },
		last_seen: { type: "date", required: false, fieldName: "last_seen" },
		anonymize_at: { type: "date", required: false, fieldName: "anonymize_at" },
		deleted_at: { type: "date", required: false, fieldName: "deleted_at" },
  	},
  },
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
});