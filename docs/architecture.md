# MaintAI architecture decisions

## Decisions

- **One serialized sklearn artifact.** Feature engineering, encoding, scaling, classifier, and calibration travel together, preventing training-serving skew.
- **SQLite persistence.** The demo needs durable history and alerts but not a network database. SQLAlchemy keeps a future migration path open.
- **Polling every three seconds.** Six simulated machines do not justify WebSocket infrastructure; polling is reliable and observable in browser tooling.
- **Transition alerts.** An alert is emitted only when an asset enters a `HIGH` or `CRITICAL` state, preventing per-reading alert spam.
- **No failure-mode predictor.** Subtype labels are sparse, overlapping, partially inconsistent with the aggregate target, and are outcome labels that would leak the primary target.
- **Model-agnostic local perturbations.** Each input is replaced by its training median/mode to estimate directional probability impact. These are influence indicators, not causal explanations.

## Risk and evaluation contract

The data is split 60/20/20 using fixed-seed stratification. Candidate selection uses five-fold cross-validation only within the 60% training partition. The selected model is fitted there and sigmoid-calibrated on the 20% validation partition. The maintenance threshold is also selected on validation by maximizing F2 subject to precision of at least 0.25. The final 20% test partition is touched once for reported metrics.

The validation partition serves both calibration and threshold selection. For a dataset of this size, this is a practical portfolio compromise. A real deployment should use nested cross-validation or a larger dedicated calibration partition and validate prospectively on equipment-specific temporal data.
