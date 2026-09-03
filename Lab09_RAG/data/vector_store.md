# Vector store

The source memory's vectors live in an embedded vector store on the ingestion host —
in-process, persisted to local disk, no separate server to operate.

## Index

The store maintains an **HNSW** index (Hierarchical Navigable Small World graph) over
all chunk vectors. The construction parameter M is set to 16 links per node; the search
beam **efSearch defaults to 96**, which our recall measurements place at 0.98 recall@10
against an exact brute-force scan. Raising efSearch widens the candidate beam: recall
rises, and latency rises with it.

## Memory footprint

The graph is RAM-resident. At the current embedding width the index costs roughly
1.2 GB of RAM per million vectors, dominated by the raw float32 vectors plus graph links.

## Deletions and rebuilds

Deletes are handled with **tombstones**: a deleted chunk is marked and filtered out of
results at query time, but physically remains in the graph until the next rebuild. The
index is **rebuilt every Sunday at 03:00 UTC**, which removes accumulated tombstones.
Operational rule since incident INC-2431: if the tombstone share exceeds 20 percent of a
collection between rebuilds, an early rebuild is triggered, because heavy tombstoning
measurably degrades recall.

## Fallback

Collections below 50,000 vectors skip HNSW entirely and use an exact NumPy scan — at
that size brute force answers in a few milliseconds and is exactly correct.
