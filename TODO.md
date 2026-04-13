## Diane

## Elroy

## Noah

## Petya
1. Major(2pts): implement rag for the ai feature: expected complition date around: 25 april: 

2. Major(2pts): llm system interface:
-> 5 3 and bananas. parsing to fix
-> swap history display: top last message: prepend to top on chat
->history with db: 
sudo docker compose exec postgres psql -U postgres -d transcendance_db -c "
CREATE TABLE IF NOT EXISTS messages (
    id         SERIAL      PRIMARY KEY,
    session_id UUID        NOT NULL,
    role       VARCHAR(10) NOT NULL --(role IN ('user', 'assistant')),
    content    TEXT        NOT NULL,
    created_at TIMESTAMP   NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_messages_session
    ON messages (session_id, created_at DESC);
"

Verify it worked:
sudo docker compose exec postgres psql -U postgres -d transcendance_db -c "\d messages"
============
for deployment:
sudo docker compose cp db/migrations/001_create_messages.sql postgres:/tmp/
sudo docker compose exec postgres psql -U postgres -d transcendance_db -f /tmp/001_create_messages.sql
docker compose cp copies from host → container, then -f works because the file exists inside the container.

Q 1: Hi, where do you hear me?
I process your text input via this interface. I do not hear audio.

Q 2: I am 53 years old.
Under stood. How can I help you today?

Q 3: How old are you and how old am I?
I am an AI without an age. You are 53.

Q 4: How old am I?
You are 5 3.
=====================