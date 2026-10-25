# Synthetic datasets for the memory pilots

Both files are frozen copies of the data used in
[`../README.md`](../README.md). They are synthetic; no real user data is
included. License: **CC BY 4.0** (see [`/DATA_LICENSE.md`](../../../DATA_LICENSE.md)).

## `conflict_pairs_50.json`

50 fact pairs for supersede-vs-insert judging.

| Field | Meaning |
|---|---|
| `id` | `P01`–`P20` (expected `SUPERSEDE`) or `N01`–`N30` (expected `INSERT`) |
| `old` | the existing session fact |
| `new` | the incoming record |
| `expected` | `SUPERSEDE` or `INSERT` |
| `category` | continuation, revision, preference_update, same_file_different_goal, different_people, uncertain, different_period, … |

Regenerate: `python export_data.py` from the parent directory.

## `deletion_profiles_50.json`

50 persistent-memory profiles for post-deletion recovery tests.

| Field | Meaning |
|---|---|
| `id` | `P00`–`P49` |
| `target` | the synthetic access code (`REGION-MNEMONIC-NUMBER`) |
| `background` | six always-present records |
| `distractors` | three records with unrelated codes/IDs |
| `exposed_record` | the target-bearing record (the one deleted in the forget world) |
| `neutral_record` | the matched never-exposed record used in the clean world |

`seed` is 20261024; the profile targets were checked against
`results/afterdelete_hierarchical_50.json` before this file was written.

Regenerate: `python export_data.py`.

## What these datasets do not establish

They are small, synthetic, and authored for a pilot. They do not estimate
production rates, and they do not validate the upstream memory systems. See the
limits section of the write-up.
