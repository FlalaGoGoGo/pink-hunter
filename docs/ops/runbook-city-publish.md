# Runbook: Targeted City Publish

## Purpose
- Add or refresh one or more cities without running the full ETL path.

## Command
```bash
./scripts/ops_runner.sh publish-city --city "Los Angeles"
```

## Standard Sequence
1. Review [City Coverage Tracker](../research/city-coverage-tracker.md) and confirm the city is in `A2` before a straightforward publish, or `B` if this task is specifically to unblock it.
2. Confirm the city has an official public single-tree dataset and official boundary.
3. Review [City ETL Methods](../research/city-etl-methods.md) and [Methodology And Pitfalls](../research/methodology-and-pitfalls.md).
4. Run the targeted publish command.
5. Refresh coverage or shard metadata if required.
6. Run the size gate.
7. Update the coverage tracker and any new source-method notes.

## Required Writeback
- Update `docs/research/city-coverage-tracker.md`
- Update `docs/research/city-etl-methods.md` when a new source family or parsing rule is introduced
