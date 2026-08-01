# Schema drift and contract mismatch

Confirm the declared contract version, the producer release, and the first failing run. Compare expected and observed fields before changing consumers. A rename must be treated as a breaking change unless an explicit compatibility mapping exists. Block downstream publication when a required field is absent. Test the revised mapping against a representative regression set, then obtain approval before a backfill.
