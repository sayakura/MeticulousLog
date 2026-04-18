# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A data-only Git repository for logging espresso shots and associated equipment/bean metadata. There is no application code, build system, or tests — just structured JSON files committed over time. Data originates from a Meticulous pressure-profiling espresso machine.

## Repository Structure

- `shots/<YYYY-MM-DD>/shot_<timestamp>.json` — Individual shot logs (multi-MB, ~195k lines each due to high-frequency sampling). Use `offset`/`limit` when reading; do not attempt to read entire files.
- `logs/` — Older shot logs (pre-2026-04-09) stored flat without date subdirectories. Same format as `shots/`.
- `meta/shot-meta.json` — Metadata keyed by shot UUID: rating (1-10), tasting notes, bean/grinder/basket/puck-screen references (by ID), and grind setting.
- `beans/beans.json` — Array of bean entries (id, name, roaster, roast date/level, tags, notes).
- `grinders/grinders.json` — Array of grinder entries (id, name, brand, burr type).
- `baskets/baskets.json` — Array of filter basket entries (id, name, size, type).
- `puck-screens/puck-screens.json` — Array of puck screen entries (id, name, size, type).

## Shot File Structure

Top-level keys: `startedAt`, `profile`, `profileId`, `status`, `sensors`, `actuators`, `endedAt`, `duration` (ms), `datapoints`.

The `status` array is the main time-series data — one entry per sample with:
- `time` / `profileTime` — elapsed time
- `state` — e.g. `"brewing"`
- `sensors` — `p` (pressure, bar), `f` (flow, mL/s), `w` (weight, g), `t` (temperature, °C), `g` (goal/target)
- `setpoints` — `active` field (null or e.g. `"temperature"`) plus the target value
- `extracting` — boolean

The `sensors` array at top level contains raw machine diagnostics (temperatures at multiple points, motor stats, etc.) — much more verbose than the `status` sensor readings.

## Data Relationships

Shot-meta entries reference equipment by UUID:
- `beanId` → `beans/beans.json[].id`
- `grinderId` → `grinders/grinders.json[].id`
- `basketId` → `baskets/baskets.json[].id` (optional — not all entries have this)
- `puckScreenId` → `puck-screens/puck-screens.json[].id` (optional — not all entries have this)
- `grindSetting` — stored as a string (e.g. `"1.2"`)

Shot-meta keys are shot UUIDs. The corresponding shot files are matched by the `startedAt` timestamp, not the UUID directly (the UUID does not appear inside the shot JSON file).

## Commit Conventions

Commits follow a consistent prefix pattern:
- `shot: <date> <time>` or `shot: <date> backfill` — Adding shot data
- `shot-meta: update` — Updating shot metadata (ratings, notes, grind settings)
- `bean: add <name>` or `bean: update <name>` — Bean entries
- `basket: add <name>` or `basket: update <name>` — Basket entries
- `grinder: add <name>` — Grinder entries
- `puck-screen: add <name>` or `puck-screen: update <name>` — Puck screen entries

## Key Details

- Notes in shot-meta are written in a mix of English and Chinese.
- The `logs/` directory contains earlier data that was later reorganized into `shots/<date>/` subdirectories.
- When analyzing shot data programmatically, use `python3` with `json` module — all data is valid JSON.
