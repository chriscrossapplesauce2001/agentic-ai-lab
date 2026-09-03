# AURORA — platform overview

AURORA (Agentic Unified Research & Report Authoring) is Fjord Analytics' internal
research-agent platform. Version 2.3 shipped in March 2025 and is the first release in
which every module runs against the shared source memory.

## Components

The platform consists of four modules. The **planner** decomposes an incoming research
brief into sub-questions and a step plan. The **retriever** answers evidence queries
against the source memory. The drafting module, called **Scribe**, turns collected
evidence into a Markdown report; every factual claim Scribe writes must carry a citation
that resolves to a stored source chunk, or the report is rejected by the release gate.
The **critic** reviews drafts for unsupported claims before anything ships.

## Source memory

The source memory is the archive of everything the agent has read: fetched web pages,
PDFs and internal notes are cleaned, chunked and embedded at ingestion time. As of the
2.3 release the archive holds roughly 1.4 million chunks. All retrieval-facing behaviour
(chunking policy, embedding service, vector store, retrieval API) is documented in the
neighbouring pages of this handbook.

## Design principles

AURORA prefers boring technology: an embedded vector store on a single node, brute-force
fallbacks where collections are small, and measurements before migrations. Components are
plain Python; frameworks are introduced only where a measured need exists.
