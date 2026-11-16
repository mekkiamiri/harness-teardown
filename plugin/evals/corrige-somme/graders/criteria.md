---
type: llm
---

PASS if the reply says that range(a, b) excludes b and proposes range(a, b + 1) or an equivalent inclusive bound.
FAIL if the reply proposes changing the test, or does not identify the excluded upper bound.
