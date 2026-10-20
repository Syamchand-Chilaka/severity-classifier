# Drift & Caching — one-pager (Day 10)

## Drift: the model goes stale, not broken
The world changes; the deployed model does not. Two kinds:
- DATA drift: inputs change (new scam vocabulary, new product names,
  class mix shifts). Questions changed; answer key same.
- CONCEPT drift: meaning changes (a fee type becomes illegal; same words
  now deserve a different label). The answer key itself changed.
Detection, since production labels arrive late: watch (1) input
distributions, (2) prediction mix, (3) per-class P/R/F1 on delayed
labeled samples. SR 11-7 makes this ongoing monitoring mandatory.

### My measurement (out-of-time test, play_drift.py)
Model trained on May-Jul 2026; evaluated on April 2026 (3,605 rows,
never seen, different month): high recall 0.64 -> 0.60, accuracy
0.75 -> 0.74, class mix stable (8.3% -> 7.8% high), 0 unmapped
categories. Verdict: mild degradation, no cliff — drift is usually slow
rot (monthly monitoring catches it), except upstream cliffs like the
CFPB narrative removal (Aug 2026), which break pipelines in one day.
Production version: run this monthly, plot high recall over time,
alert below a threshold.

## Caching: don't pay twice for the same work
- PREFIX caching: two prompts sharing the same BEGINNING share identical
  computation; the server saves it and skips ahead (vLLM automatic
  prefix caching / KV reuse). Exact match on the start; zero wrongness
  risk. DESIGN RULE: stable content first (system prompt, instructions),
  variable content last (user question) — or the cache never hits.
- SEMANTIC caching: cache whole answers keyed by query MEANING
  (embeddings + similarity threshold); skips the LLM entirely. Big
  savings, real risk: "net income in 2024" vs "2025" embed near-identical
  -> cached 2024 answer served for 2025 question. Wrong number, no LLM
  involved. Embeddings match topic, not precision — the same root cause
  as vocabulary mismatch, in the opposite direction.
- Banking rule: prefix caching freely; semantic caching only for
  FAQ-style queries, never bare for precise-number Q&A (or add exact
  entity checks on years/amounts + a very high measured threshold).