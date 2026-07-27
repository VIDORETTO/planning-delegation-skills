---
name: <skill-name-kebab-case>
description: <What to use this skill for>. Use when <trigger condition>. Do not <explicit exclusion, to keep the boundary legible>.
---

# <Human-Readable Skill Title>

<One short paragraph: what this skill produces and why it exists as its own skill rather than as
part of a neighbor.>

## Required resources

1. Read `references/<topic>.md` before <step>.
2. Use `assets/<ARTIFACT>.template.md` for <artifact>.
3. Run `scripts/validate_<stage>.py` before <claiming readiness>.

## Exclusive ownership

<What this skill owns exclusively, and the explicit instruction to stop after its own stage instead
of silently continuing into a neighbor's responsibility.>

## Entry gate

| Situation | Required action |
|---|---|
| <allowed incoming state> | <what to do> |
| Any other status owned by another skill | Stop without modifying artifacts |

## Method

### 1. <First step>

<...>

## Output contract

Produce only <exact artifact list>. Do not claim completion unless validation succeeds.

## Prohibitions

- Do not <exclusion 1>.
- Do not <exclusion 2>.
