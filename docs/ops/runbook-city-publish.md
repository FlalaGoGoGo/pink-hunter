# Runbook: Targeted City Publish

## Purpose
- Add or refresh one or more cities without running the full ETL path.

## Command
```bash
./scripts/ops_runner.sh publish-city --city "Los Angeles"
```

## Standard Sequence
1. Confirm the city has an official public single-tree dataset and official boundary.
2. Review [City ETL Methods](../research/city-etl-methods.md) and [Methodology And Pitfalls](../research/methodology-and-pitfalls.md).
3. Run the targeted publish command.
4. Refresh coverage or shard metadata if required.
5. Run the size gate.
6. Update the coverage tracker and any new source-method notes.

## Required Writeback
- Update `docs/research/city-coverage-tracker.md`
- Update `docs/research/city-etl-methods.md` when a new source family or parsing rule is introduced
