# Dry Run Scope

Run: `2026-06-07_12-59-22_kitchen-help-dry-run`

## Purpose

Verify that the `/astory` idea-room pathway works as an agentic planning system and stops before final image generation when identity/style references are missing.

## Included

- input parsing
- setup/reference gate
- three-agent idea room
- merged idea board
- scoring
- selected idea
- rejected ideas
- idea engagement report
- audit summary

## Excluded

- final prompt lock
- built-in imagegen
- image QA room
- final carousel exports

## Expected Final Status

`planning_ready_imagegen_blocked`
