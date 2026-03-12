import type { RequestHandler } from '@sveltejs/kit';

let questions = [
  {
    id: 1,
	projectname: 'How to use SvelteKit with TypeScript?',
    topic: 'CSS',
    body: 'I tried using margin:auto but it does not work'
  }
];

export const GET: RequestHandler = async () => {
  return new Response(JSON.stringify(questions), {
    headers: { 'Content-Type': 'application/json' }
  });
};

export const POST: RequestHandler = async ({ request }) => {
  const { projectname, topic, body } = await request.json();
  const newQuestion = { id: Date.now(), projectname, topic, body };
  questions = [newQuestion, ...questions]; // new questions at top
  return new Response(JSON.stringify(newQuestion), {
    headers: { 'Content-Type': 'application/json' }
  });
};