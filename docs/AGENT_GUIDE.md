# Building an Agent

This guide walks through creating a new agent step by step.

## Prerequisites

- Read [AGENTS.md](AGENTS.md) first
- Understand the tool framework
- Understand `AgentContext` and `AgentResult`

## Step 1 — Choose a responsibility

Each agent should have **one clear responsibility**. Examples:

- ✅ "Analyze resumes and extract skills"
- ✅ "Generate interview questions for a target role"
- ❌ "Do everything career-related" (too broad)
- ❌ "Call an LLM and return whatever" (too vague)

## Step 2 — Decide which tools you need

Agents can ONLY use tools in their `allowed_tools` allowlist.
Choose the **minimum** set of tools required.

```python
allowed_tools = frozenset({"resume_reader", "skill_extractor"})