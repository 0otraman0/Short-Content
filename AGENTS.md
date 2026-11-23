# AGENTS.md - read this first, every session

You have no memory between sessions. The files in this repo are your memory.
At the start of a session read ONLY STATE.md (AGENTS.md loads automatically). Then read just the task you are about to do in PLAN.md and the R items it lists in SPEC.md. Do not read anything else unless the task needs it.

## Files
- STATE.md = current state snapshot (max 15 lines). Read first.
- SPEC.md = what to build (numbered requirements R1, R2...). Source of truth. NEVER edit unless I explicitly say so.
- PLAN.md = tasks T1, T2... Each task: goal, files it may touch, requirements covered (R#), owner role, status (todo/doing/done/blocked), how to test it.
- DECISIONS.md = technical choices and the reason. Append only.
- CHANGELOG.md = what each finished task changed.

## Roles (use the Swarm plugin to run them as separate agents if available; otherwise act as each role in turn)
1. Planner: reads SPEC.md, writes and updates PLAN.md, splits work into small tasks. Writes no code.
2. Builder: takes ONE task, edits ONLY the files listed for it, runs its test, marks it done.
3. Reviewer: checks the finished task against SPEC.md and its test, reports problems. Does not rewrite unrelated code.

## Rules
- One task at a time. Start the next only after the previous test passes.
- Do not touch files outside the task's file list. If you must, write a note in PLAN.md and ask me first.
- If my request conflicts with SPEC.md, stop and ask me. Do not silently change the plan.
- Fix bugs with the smallest possible change. Never rewrite a whole module to fix a small bug.
- After each task: update PLAN.md status, add a line to CHANGELOG.md, make a git commit, then summarize in Vietnamese in 3-5 lines and tell me how to test it.
- Windows only: use pathlib, no bash-only commands.
- Free tools only. The only external API allowed is Gemini (free key in .env).

## Reading budget
- Do NOT read CHANGELOG.md or DECISIONS.md at the start. Read them only when a task needs them.
- Read only the "doing" task (or the next "todo" task) in PLAN.md, and only the R items it lists in SPEC.md.
- Read code files only if they are in the task's file list.

## STATE.md
After EVERY task (and when I say "token is running low"), overwrite STATE.md with the current state, max 15 lines. This file is the only thing a new chat must read first.
At the start of a session read ONLY STATE.md (AGENTS.md loads automatically). Then read just the task you are about to do in PLAN.md and the R items it lists in SPEC.md. Do not read anything else unless the task needs it.
