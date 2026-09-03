# Retrieval API

The retrieval API is the tool surface the agent calls; the model decides when to search
and with which query.

## search_sources

`search_sources(query, k)` embeds the query, runs the index search, and returns chunk
text, source URL and similarity score per hit. **k defaults to 6.** The similarity score
is returned, not hidden, so the agent's assess step can see when the best hit is weak
and decide to reformulate the query.

## Hybrid retrieval

Dense and lexical retrieval fail differently, so the API runs both: an HNSW search over
embeddings and a BM25 search over an inverted index. The two candidate lists are merged
with **reciprocal rank fusion using the constant c = 60** — fusion is by rank, not by
score, because BM25 scores and cosine similarities live on incomparable scales.

## Reranking

The fused top 40 candidates are rescored by a cross-encoder reranker, which reads query
and chunk together; the **best 5 survive** into the generation prompt. This is the
two-stage shape: cheap recall over the whole archive, expensive precision over a short
list.

## Latency budget

The end-to-end retrieval budget is **120 ms at the 95th percentile** per query, measured
weekly on a fixed evaluation query set.
