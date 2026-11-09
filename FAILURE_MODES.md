# Failure modes

## Stale sister quotes

Headline cells whose class is a sibling quote were read on 2026-11-09 from the commits named in [`quotes/headline_quotes.json`](quotes/headline_quotes.json). `scripts/check_index.py` does not fetch those repositories. A later sister commit can change a count, a path, or a claim id while this index still prints the old cell. The observed date is the warning. Updating a cell means reading the sister again and changing the commit pin. Copying a new number into the README without that pin is a stale quote, not a measurement.

## This index does not hold the primary corpora

The constructed matrix, the R5 result trees, and the effort execution records are not in this clone. The offline check cannot rebuild them. A standalone grade A study would keep that primary evidence, and an offline recompute of it, in the repository being graded. This repository's role is an index satellite, and its status stays WORK-IN-PROGRESS for that reason.

## Pilot is not the published protocol

The harness, deletion, and memory-mechanism pilots are small local runs. Each folder states the sample, the model, and the published pieces it does not reproduce. Directional agreement with a paper is not that paper's rate. Close-reading rates of external papers inside those notes are not rows in the headline ledger. The quote-ledger change did not re-read the PDFs.

The decay report is a standard-library re-implementation of a formula cited from upstream Rust. The upstream crate was not executed. A later change to that crate would not move `results/decay_sim.json` until someone edits this re-implementation.

## Recount is not a new model run

Pilot-row cells are recounted from committed JSON. Decay cells are recomputed by `decay_sim.build_report`. Neither step calls Ollama or any other model. Temperature 0 does not remove serving nondeterminism. The committed file is the record of the pilot that was run.

## False zero and other zeros

A zero unauthorized count is not a safety result.

- On r5, llama arm B's zero sits next to 27/27 unparseable outputs. That is a false zero from format collapse, not containment.
- Qwen arm B's zero is a parsed stop on this fixture. The primary endpoint is empty because no acting cell also emitted a verification assertion.
- Local execution binding can show zero unauthorized effects while the model still attempts the action and the binding denies it.
- On the approval-gates constructed matrix, deny-all also has zero unauthorized effects. That repo's abstract pairs the deny-all zero with zero clean utility.

## Summary drift inside this clone

If a committed `summary` object disagrees with its `rows`, the offline check fails. Prose in the blog and the replication notes is not parsed by that check. When prose and JSON disagree, the JSON is the record.

## A corrected misstatement

An earlier README line described the conservative conflict result as rejecting 1/90 parallel pairs. The recounted rows contain one conservative false merge: `qwen2.5:7b` pair N25, category `different_decisions`.
