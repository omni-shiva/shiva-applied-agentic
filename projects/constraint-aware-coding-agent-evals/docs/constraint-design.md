# Constraint design

The sample uses six independently observable behaviors from deliberately different failure categories. This diversity is an authored design choice, not a formal proof that every possible implementation error is statistically independent.

| ID | Behavior category | Obvious violation | Subtle near miss |
|---|---|---|---|
| `consume-input-once` | Input protocol | Two loops over the input | A preflight pass followed by classification |
| `preserve-rejected-identity` | Object ownership | Deep-copy each reject | Reconstruct it with a convenience helper |
| `do-not-mutate-inputs` | State integrity | Rewrite the channel | Temporarily modify nested metadata |
| `snapshot-clock-once` | Time consistency | Call the clock in the loop | Call it separately in delegated helpers |
| `delegate-channel-resolution` | Dependency boundary | Use a local allowlist | Call the policy but ignore its result |
| `preserve-rejection-order` | Stable ordering | Sort rejected items | Group rejection reasons and concatenate them |

Each constraint is paired with a focused probe and at least one accepted and single-fault adversarial fixture. The validator confirms that every adversarial fixture fails only the intended probe. The clock probe uses controlled real-datetime behavior, with accepted direct, inverse, arithmetic, and timestamp variants. A separate accepted variant protects valid extra policy lookups. Additional regressions cover transient mutation, ignored clock values, hybrid and call-then-ignore dependency logic, incomplete outputs, and duplicated originals.

The comparison candidate is a realistic near-miss, not random broken code. It passes the ordinary value tests while combining four behavior violations.
