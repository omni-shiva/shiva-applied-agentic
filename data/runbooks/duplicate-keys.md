# Duplicate keys and join explosion

Measure key uniqueness before the join and compare input, matched, unmatched, and output cardinalities. Quarantine violating keys so a clean subset can be assessed safely. Do not hide the problem with a blanket drop-duplicates step unless the business rule defines which record wins. Add a contract-level uniqueness assertion and a regression case for the failure pattern.
