# Evaluation report: notice-planner-001

All data and results in this report are synthetic.

| Run | Functional tests | Constraint compliance | Fully passed |
|---|---:|---:|---:|
| Synthetic reference | PASS | 100.0% (6/6) | PASS |
| Synthetic comparison | PASS | 33.3% (2/6) | FAIL |

Compliance separation: **66.7%**

Functional correctness alone is insufficient: both runs pass tests, but their independently measured constraint compliance differs.

## Constraint-level evidence

### Synthetic reference

- PASS `consume-input-once`: source iteration count=1
- PASS `preserve-rejected-identity`: original identities preserved=True; rejected count=2
- PASS `do-not-mutate-inputs`: object writes=0; nested writes=0; final state restored=True
- PASS `snapshot-clock-once`: clock calls per invocation=[1, 1]; early rejected=['between']; early delivered=['already-ready']; late rejected=[]; late delivered=['between', 'already-ready']
- PASS `delegate-channel-resolution`: policy configurations=[{'inputs_observed': True, 'batches_match': True, 'rejected_match': True, 'rejected_ids': ['text', 'fax']}, {'inputs_observed': True, 'batches_match': True, 'rejected_match': True, 'rejected_ids': ['mail', 'carrier-pigeon']}]
- PASS `preserve-rejection-order`: rejected ids=['future-1', 'unsupported-1', 'future-2', 'unsupported-2']; relative order preserved=True

### Synthetic comparison

- FAIL `consume-input-once`: probe raised RuntimeError: input iterable was consumed more than once
- FAIL `preserve-rejected-identity`: original identities preserved=False; rejected count=2
- FAIL `do-not-mutate-inputs`: object writes=1; nested writes=0; final state restored=False
- FAIL `snapshot-clock-once`: clock calls per invocation=[2, 2]; early rejected=['between']; early delivered=['already-ready']; late rejected=[]; late delivered=['between', 'already-ready']
- PASS `delegate-channel-resolution`: policy configurations=[{'inputs_observed': True, 'batches_match': True, 'rejected_match': True, 'rejected_ids': ['text', 'fax']}, {'inputs_observed': True, 'batches_match': True, 'rejected_match': True, 'rejected_ids': ['mail', 'carrier-pigeon']}]
- PASS `preserve-rejection-order`: rejected ids=['future-1', 'unsupported-1', 'future-2', 'unsupported-2']; relative order preserved=True
