# Synthetic notice planner example

This fictional Python scenario demonstrates why returned values and implementation behavior should be evaluated separately.

Both authored candidates pass the ordinary tests. The reference also passes six focused runtime probes. The intentionally flawed comparison violates iterable, identity, mutation, and time-snapshot constraints while still producing the expected ordinary values.

The example contains a starter fixture, six behavior constraints, reproducible reference evidence, twelve isolated adversarial probe fixtures, two functional-decoupling fixtures, and two authored candidate runs. No external model produced these artifacts.
