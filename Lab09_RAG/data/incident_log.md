# Incident log (excerpts)

## INC-2417 — error QF-5501 in the ingestion service

Symptom: newly ingested documents were never retrieved; queries returned only old
chunks. The ingestion service logged **error QF-5501** on every batch. Root cause: an
**embedding model version mismatch** — the ingestion host had been upgraded to a newer
borealis-embed version while the query path still ran the old one, so new document
vectors and query vectors lived in misaligned geometries. Nothing crashed; retrieval
silently returned noise for new content. Fix: pin the embedding model version in both
paths, add a startup check, and re-embed the affected corpus with the pinned version.

## INC-2431 — recall regression after bulk delete

Symptom: recall@10 on the weekly evaluation set dropped from 0.98 to 0.91 with no
deployment in between. Root cause: a bulk GDPR deletion had tombstoned 23 percent of one
collection, degrading the connectivity of the HNSW graph. Fix: immediate index rebuild;
a new operational rule triggers an early rebuild whenever the tombstone share exceeds
20 percent.

## INC-2440 — refusal path regression

Symptom: for questions outside the corpus, the drafting module produced fluent,
cited-looking answers instead of declining. Root cause: a prompt refactor had dropped
the refusal instruction from the system rules. Fix: restore the instruction — if the
sources do not contain the answer, say so — and add an unanswerable-query suite to the
weekly evaluation.
