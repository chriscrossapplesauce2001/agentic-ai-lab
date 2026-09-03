# Ingestion pipeline

The ingestion pipeline turns fetched sources (web pages, PDFs, internal notes) into
retrievable chunks. It runs offline, once per document; throughput matters, latency
does not.

## Cleaning and deduplication

Boilerplate — navigation, cookie banners, advertisements — is stripped before chunking.
Near-duplicate chunks are dropped when their cosine similarity to an already stored
chunk exceeds **0.97**, so that a single popular page cannot dominate the top-k of every
query.

## Chunking policy

Documents with markup are chunked **structurally** at heading and paragraph boundaries.
The target chunk length is **220 tokens**; sections longer than twice the target fall
back to fixed-size windows with **15 percent overlap**, so that sentences severed at a
window boundary survive intact in the neighbouring chunk.

## Contextual enrichment

Each chunk is prepended with a short context line — the page title, the source URL and
the retrieval date — before embedding. Isolated chunks otherwise lose their document
context: "revenue grew nine percent" is neither retrievable nor interpretable without
knowing which company and which year.

## Metadata

Every chunk record carries the source URL, the retrieval date, and a stable chunk id.
The URL travels with every retrieval result so that Scribe can cite it mechanically;
the retrieval date feeds staleness checks.
