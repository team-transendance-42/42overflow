-- RAG QAPair seed — topics NOT covered by any JSON seed file.
-- Topics: push_swap, minishell, webserv
--
-- Fields used by the RAG pipeline: question, answer, topic, tags
-- source: stored for future admin tooling, not read by retrieval today
--
-- Safe to re-run: ON CONFLICT (question) DO NOTHING
--
-- How to run:
--   psql postgresql://postgres:postgres@localhost:5433/transcendance_db \
--        -f prisma/seed-qa-pairs.sql
--
-- Or inside the running container:
--   docker compose exec postgres \
--     psql -U postgres transcendance_db \
--     -f /dev/stdin < prisma/seed-qa-pairs.sql
--
-- After running, restart python-rag to re-embed and re-index:
--   docker compose restart python-rag
--   docker compose logs python-rag -f   # wait for "ChromaDB sync complete"

-- ─── push_swap ───────────────────────────────────────────────────────────────

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'What sorting algorithm does push_swap use for large stacks and why is it optimal for that range?',
  'push_swap uses a chunk-based approach for large stacks (100 or 500 elements). The stack is divided into value-range chunks; elements in the current chunk are pushed to stack B in roughly sorted order using ra/rb rotations to find the cheapest target position. Chunk size is tuned experimentally — chunks of 30-40 elements minimise total move count. For 100 elements the moulinette requires under 700 operations; for 500 elements under 5500. Pure insertion sort is O(n^2) and fails these limits above ~20 elements. The chunk approach achieves O(n log n) equivalent move counts because each element is placed roughly sorted in B, requiring only a final push-back pass to A.',
  'push_swap',
  ARRAY['sorting', 'chunk-sort', 'optimization', 'large-stack', 'moulinette'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'In push_swap with exactly 3 elements, what is the maximum number of operations needed and what are the six cases?',
  'Sorting 3 elements [a, b, c] where a<b<c requires at most 2 operations. The 6 orderings: [a,b,c] already sorted — 0 ops. [b,a,c] — sa, 1 op. [a,c,b] — rra, 1 op. [c,a,b] — ra, 1 op. [b,c,a] — ra then ra, 2 ops. [c,b,a] — sa then rra, 2 ops. Worst case is always 2 operations. The moulinette tests 3-element sort with this exact limit. A common mistake is implementing [b,c,a] as sa→rra which gives [a,c,b] not [a,b,c] — verify each case manually before submitting.',
  'push_swap',
  ARRAY['3-elements', 'small-stack', 'cases', 'optimal', 'moulinette'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'How does push_swap sort exactly 5 elements and what is the maximum allowed operation count?',
  'For 5 elements push_swap must sort in at most 12 operations. Standard approach: push the two smallest elements to B (pb pb), sort the remaining 3 on A using the 3-element algorithm (at most 2 ops), then push back from B inserting each element at the correct A position using ra/rra to find the cheapest slot. The key insight is that pa with rotations is cheaper than full in-place sorting. Moulinette limits: 2 elements = 1 op max (sa), 3 = 2 ops, 5 = 12 ops. Students who use a generic large-stack algorithm for all sizes often pass 500-element tests but fail the small-stack requirements because the generic algorithm is not operation-optimal for small n.',
  'push_swap',
  ARRAY['5-elements', 'small-stack', 'pb', 'pa', 'moulinette', 'optimal'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'What is the difference between ra and rra in push_swap and when do you use each?',
  'ra (rotate a) moves the top element of stack A to the bottom. rra (reverse rotate a) moves the bottom element of stack A to the top. Same operations exist for B: rb, rrb. Combined rotations rr (ra+rb simultaneously) and rrr (rra+rrb simultaneously) each count as 1 operation. ra is used to bring a target position to the top of A when inserting from B. rra is used when the target is closer to the bottom. Cost calculation: cost_ra = position_in_a steps forward, cost_rra = size_a - position_in_a steps backward. Always pick the cheaper direction. When positioning an element in B before pushing, apply the same min-cost logic with rb/rrb. Using rr/rrr to move both stacks simultaneously is the key optimisation that brings 500-element sort under the 5500-operation limit.',
  'push_swap',
  ARRAY['ra', 'rra', 'rotate', 'cost-calculation', 'rr', 'rrr', 'optimization'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

-- ─── minishell ───────────────────────────────────────────────────────────────

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'How does minishell handle heredoc and why must it fork before reading heredoc input?',
  'A heredoc (<< DELIMITER) reads lines from stdin until a line matching DELIMITER appears, then makes that content the command stdin. Minishell must fork before reading heredoc input for two reasons: (1) the parent shell must not block on readline — Ctrl+C during heredoc input should kill only the reader, not the shell itself; (2) SIGINT during heredoc reading should cancel only the heredoc, not terminate the shell. Correct implementation: fork a child that reads lines into a pipe write-end, parent waitpid; if child is killed by SIGINT (WIFSIGNALED && WTERMSIG==SIGINT), abandon the heredoc and print a newline, matching bash behavior. The pipe read-end becomes the command stdin after the child exits cleanly.',
  'minishell',
  ARRAY['heredoc', 'fork', 'SIGINT', 'pipe', 'signal-handling', 'readline'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'How does minishell implement pipes between commands and what file descriptor management is required?',
  'Each pipe creates two FDs via pipe(). For cmd1 | cmd2 | cmd3: (1) create all pipes before forking; (2) fork each child; (3) cmd1 child: dup2(pipe1[1], STDOUT_FILENO), close all unused FDs; (4) cmd2 child: dup2(pipe1[0], STDIN_FILENO) + dup2(pipe2[1], STDOUT_FILENO), close all unused FDs; (5) cmd3 child: dup2(pipe2[0], STDIN_FILENO), close all unused FDs; (6) parent closes ALL pipe FDs then waitpid all children. Critical: the parent MUST close both ends of every pipe after forking. If the parent keeps the write-end open, cmd2 and cmd3 never receive EOF on stdin — the pipeline hangs forever. Forgetting to close pipe FDs in the parent is the most common minishell bug.',
  'minishell',
  ARRAY['pipe', 'fork', 'dup2', 'file-descriptor', 'EOF', 'pipeline', 'waitpid'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'How must minishell handle SIGINT and SIGQUIT differently in interactive mode versus inside a child process?',
  'Interactive mode (no running command): SIGINT prints a newline and shows a fresh prompt (Ctrl+C behavior). SIGQUIT is ignored (SIG_IGN) — bash ignores Ctrl+\ interactively. Inside a running child: child must use DEFAULT signal handlers (SIG_DFL). The parent sets custom handlers before fork; the child resets them to SIG_DFL immediately after fork and before execve. Exit status after SIGINT: 130 (128 + signal 2). After SIGQUIT: 131 (128 + 3). Set from waitpid result: status = 128 + WTERMSIG(wstatus). Using signal() in the parent and expecting children to inherit correct behavior does not work — you must explicitly call sigaction with SIG_DFL in the child.',
  'minishell',
  ARRAY['SIGINT', 'SIGQUIT', 'sigaction', 'SIG_DFL', 'exit-status', 'interactive', 'fork'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'How does minishell expand environment variables inside double quotes and what are the edge cases?',
  'Inside double quotes, $VAR and ${VAR} expand to the environment value. $? expands to the last exit status. Single quotes suppress all expansion. Edge cases: (1) $UNDEFINED expands to empty string — the token shrinks, not to literal "$UNDEFINED"; (2) "$VAR" with spaces in VAR does NOT word-split — quotes protect it, producing one argument; (3) unquoted $VAR with spaces DOES word-split into multiple tokens; (4) $123 (starts with digit) expands to empty — positional parameters not required by the subject; (5) contiguous tokens: echo "hello"$VAR"world" must concatenate into one argument. The most common bug is word-splitting after expansion even inside quotes, producing extra arguments the evaluator does not expect.',
  'minishell',
  ARRAY['expansion', 'double-quotes', 'environment-variable', 'word-split', 'dollar', 'edge-case'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

-- ─── webserv ─────────────────────────────────────────────────────────────────

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'What is CGI in webserv and how does the server pass environment variables to the CGI process?',
  'CGI (Common Gateway Interface) lets a web server execute an external program and use its stdout as the HTTP response. In webserv, when a request matches a CGI location (*.py, *.php), the server: (1) forks a child; (2) sets env vars via execve envp — REQUEST_METHOD, QUERY_STRING, CONTENT_TYPE, CONTENT_LENGTH, PATH_INFO, SCRIPT_FILENAME, SERVER_PROTOCOL; (3) pipes the request body to child stdin; (4) reads child stdout as the response. The CGI script writes its own headers, a blank line, then body. The server must enforce a timeout — kill child after N seconds and return 504 Gateway Timeout. Close all listening sockets in the child before execve so the CGI cannot accidentally accept connections.',
  'webserv',
  ARRAY['CGI', 'fork', 'execve', 'environment-variables', 'timeout', '504'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'How does webserv use select or poll to handle multiple connections without blocking?',
  'webserv handles multiple clients without threads via an event loop: (1) add all listening sockets to the interest set; (2) call select/poll/epoll_wait — blocks until at least one FD is ready; (3) for each ready FD: if listening socket, accept() and add to set; if client socket, read only what is ready (never block), parse incrementally, write response when complete. Rules: never call read() or write() without first confirming readiness — blocking stalls all other clients. No blocking syscalls (sleep, blocking DNS) inside the loop. Each client needs a state machine tracking how much of its request arrived and how much of its response was sent. The subject forbids fork-per-connection and thread-per-connection.',
  'webserv',
  ARRAY['select', 'poll', 'epoll', 'non-blocking', 'event-loop', 'multiplexing', 'state-machine'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'How does webserv parse an HTTP request and what states does the parser need?',
  'HTTP requests arrive in chunks over TCP — a single read() may deliver a partial header or multiple requests. Parser states: (1) READ_REQUEST_LINE — read until \r\n, parse method, URI, version; (2) READ_HEADERS — read until \r\n\r\n, parse "Key: Value\r\n" pairs; (3) READ_BODY — if Content-Length set, read exactly that many bytes; if Transfer-Encoding: chunked, parse chunk sizes; (4) COMPLETE — dispatch to handler. Error codes: 400 if method or version malformed; 413 Payload Too Large if Content-Length exceeds configured max_body_size; 505 if HTTP version not 1.0 or 1.1. The parser must handle \r\n\r\n split across two read() calls — the buffer must carry partial data between calls.',
  'webserv',
  ARRAY['HTTP-parsing', 'state-machine', 'request-line', 'headers', 'Content-Length', 'chunked', '400', '413'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;

INSERT INTO "QAPair" (question, answer, topic, tags, source, "createdAt", "updatedAt") VALUES (
  'What HTTP status codes must webserv implement and what are the most commonly missed ones?',
  'Required: 200 OK (GET/POST success), 201 Created (file upload via POST), 204 No Content (DELETE with no body), 301 Moved Permanently (directory without trailing slash → redirect to slash), 400 Bad Request (malformed request), 403 Forbidden (path exists, permission denied), 404 Not Found, 405 Method Not Allowed (method not in location allowed_methods), 413 Payload Too Large (body > max_body_size), 500 Internal Server Error (CGI crash), 504 Gateway Timeout (CGI timeout). Most commonly missed: 301 — if config has location /foo/ and client requests /foo, return 301 with Location: /foo/. Also missed: Content-Length must exactly match actual body size on every response with a body, including error pages.',
  'webserv',
  ARRAY['status-codes', '301', '404', '405', '413', '504', 'Content-Length', 'redirect'],
  'community-db',
  NOW(), NOW()
) ON CONFLICT (question) DO NOTHING;
