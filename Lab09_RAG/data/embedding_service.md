# Embedding service

The embedding service turns text spans into dense vectors for the source memory.

## Model

AURORA uses **borealis-embed-v2**, a retrieval-trained sentence encoder. Every text span
is mapped to a single vector of **768 dimensions**; per-token representations are
mean-pooled into one vector per span. The model was trained contrastively on
query-passage pairs, so questions and the passages that answer them land close together
even though they share little surface form.

## Asymmetric prefixes

Retrieval is asymmetric: queries and documents are embedded with distinct instruction
prefixes. Documents are prefixed with `search_document:` at ingestion time, queries with
`search_query:` at query time. Mixing the prefixes up does not raise an error — it
silently degrades retrieval quality, which is why the ingestion pipeline and the
retrieval API share one client library.

## Similarity and normalisation

All vectors are L2-normalised at creation time. Relevance is scored with cosine
similarity, which with normalised vectors reduces to a plain dot product. The service
must never mix model versions between the index and the query path: after the QF-5501
incident, the deployed model version is pinned and verified at startup.

## Throughput

Batch embedding sustains about 1,400 chunks per second on the ingestion host; single-query
embedding latency is 9 ms at the 95th percentile.
