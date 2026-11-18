# Collaborative Whiteboard

I built this real-time collaborative whiteboard as a timed take-home for Mechanize. It is meant for design reviews where 2 to 5 people on a call edit the same canvas, often the same shapes at once. It has accounts, invites, four shape types, live named cursors and per-user undo and redo, and canvases persist.

The hard part is keeping everyone consistent. Every edit is one Postgres transaction. It bumps a per-canvas sequence number under a row lock, so edits are serialized and that number becomes the shape's version. Only after the commit does the server broadcast the new row. Each client keeps the highest version it has seen, so a late or out-of-order frame can never move anything backwards. A shape's position and size are replaced as one unit, so a drag and a resize that race end as one user's shape, never a mix of both. Deletes are tombstones, so a late drag can't bring a shape back. Undo just sends the inverse of my own edit through the same path.

Before submitting, I ran a scripted test with 5 users on one canvas, firing edits at the same time: 26 of 26 checks passed on 3 runs in a row.

stack: React, TypeScript, Vite, FastAPI, WebSockets, PostgreSQL (asyncpg), Docker Compose
links:
