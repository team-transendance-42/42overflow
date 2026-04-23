
1. Core Shortcuts
Action	Shortcut
Focus between editor & Claude	Ctrl+Esc
New conversation tab	Ctrl+Shift+Esc
New conversation	Ctrl+N
Multi-line prompt	Shift+Enter
Insert @-mention of current file/selection	Alt+K
========================

 @-Mentions (Most Useful Feature)
Reference files, folders, or selections directly in your prompt:


Fix the bug in @src/routes/ai-assist/+page.svelte
Refactor @src/routes/
Explain the selected code @src/api/users.ts#15-20
Fuzzy matching works — @auth finds AuthService.ts, auth.js, etc.
=========================

Slash Commands
Type / in the prompt box:

Command	Use
/memory	View/edit your CLAUDE.md persistent instructions
/compact	Free up context window
/model	Switch between Opus / Sonnet / Haiku
/mcp	Manage MCP tool servers
/usage	View token usage
========================

Diff Review
Claude shows side-by-side diffs — you can edit the proposed code directly in the diff before accepting. You're not forced to accept or reject as-is.
========================

 Custom Skills: todo: learn more abt this
Create .claude/skills/commit/SKILL.md for repeatable workflows, then invoke with /commit. Good for git commits, PR creation, deploy steps, etc.
=======================

Pro Tips
Alt+K + describe what's wrong = fastest way to fix selected code
Use Plan mode before any large refactor
Ctrl+Esc to jump between editor and Claude without touching the mouse