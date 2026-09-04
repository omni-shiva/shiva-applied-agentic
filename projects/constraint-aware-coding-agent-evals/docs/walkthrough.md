# Reproduction walkthrough

## 1. Use the zero-install route

Python 3.11 or newer can run the project directly without downloading packages:

```bash
PYTHONPATH=src python -m agent_eval_lab validate examples/notice_planner
```

An optional editable install provides the `agent-eval` command. Depending on the Python distribution, `pip` may need to obtain standard build tooling.

## 2. Validate the probes

```bash
PYTHONPATH=src python -m agent_eval_lab check-probes examples/notice_planner
```

Expected outcome: fourteen accepted probe checks pass, twelve isolated adversarial fixtures each fail only their paired probe, and nineteen unique candidates match their declared functional-test outcomes.

## 3. Evaluate both candidates

```bash
PYTHONPATH=src python -m agent_eval_lab evaluate examples/notice_planner --output reports/generated
```

Expected outcome:

- both candidates pass the ordinary tests;
- the reference passes 6/6 behavior constraints;
- the comparison passes 2/6 behavior constraints;
- JSON and Markdown reports are written under `reports/generated`.

## 4. Run project tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 5. Check the intended public source set

```bash
python tools/check_public_release.py
python tools/check_manifest.py
```

The source scan checks configured sensitive-data patterns. It excludes development caches, environments, build outputs, and version-control history. Inspect the full Git diff separately before publishing.

## 6. Regenerate controlled artifacts after a change

```bash
python tools/generate_reference_patch.py
python tools/generate_manifest.py
```

Stage and publish this project only through the existing `shiva-applied-agentic`
repository after all checks pass. Never copy a nested `.git` directory,
pre-sanitization history, local caches, or machine-specific artifacts into the
portfolio repository.
