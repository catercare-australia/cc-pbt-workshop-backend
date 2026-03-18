# Property-Based Testing Workshop: Python/Django Backend

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/OWNER/pbt-workshop-backend?quickstart=1)

## Quick Start

1. Click **Open in GitHub Codespaces** above (or clone locally)
2. Wait for the devcontainer to build (~2 minutes)
3. Run the tests: `uv run pytest -v`
4. Start with Exercise 1!

## What This Repo Contains

An **Order lifecycle** domain implemented across three self-contained Django apps — one per exercise:

- `ex1_invariants/` — Exercise 1: Invariant properties
- `ex2_workflow/` — Exercise 2: Model-based workflow testing
- `ex3_robustness/` — Exercise 3: Robustness properties

Each exercise app has its own models, domain logic, tests, and solutions.

**You will NOT modify any domain code.** Your job is to write property-based tests that exercise the domain logic.

### Shared Utilities

- `shared/exceptions.py` — `DomainError` exception used by all exercises
- `shared/strategies.py` — Hypothesis strategies for generating test data

## Workshop Exercises

### Exercise 1: Invariants (`ex1_invariants/tests/test_invariants.py`)

Write properties that must always hold for any valid Order state.

### Exercise 2: Model-Based Workflow (`ex2_workflow/tests/test_workflow.py`)

Build a state machine that generates random action sequences and asserts the real system never diverges from a reference model.

### Exercise 3: Robustness (`ex3_robustness/tests/test_robustness.py`)

Verify that domain operations never crash unexpectedly on any valid input.

## Running Tests

```bash
# All exercises (solutions excluded by default)
uv run pytest -v

# Single exercise
uv run pytest ex1_invariants/tests/ -v
uv run pytest ex2_workflow/tests/ -v
uv run pytest ex3_robustness/tests/ -v

# Run a solution to check your work
uv run pytest ex2_workflow/solutions/ -v
```

## Key Files

| File | Purpose |
|------|---------|
| `shared/strategies.py` | Hypothesis strategies for test data |
| `ex2_workflow/tests/reference_model.py` | Reference model for workflow testing |
| `ex1_invariants/domain.py` | Domain logic under test (**DO NOT EDIT**) |

## Hints

- Look for `TODO` and `pass` in the test files
- The reference model in `ex2_workflow/tests/reference_model.py` implements the correct rules
- If a test finds a bug, read the shrunk counterexample carefully!
- Solutions are in each exercise's `solutions/` directory if you get stuck (no peeking!)
