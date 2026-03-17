# Deep Analysis — Domain Examples

## Example 1: Market / Go-to-Market Analysis

**Source materials**: 8 competitor landing pages, 3 earnings call transcripts, 12 customer reviews, 1 Reddit complaint thread.

**Phase 2 prompt**:
```
What does every successful player in this market understand
that their customers never say out loud?
```

**Phase 4 prompt**:
```
Write 5 questions a world-class VC investor would ask
to destroy this go-to-market strategy,
then answer each one using only the evidence in these documents.
```

---

## Example 2: Technical Architecture Decision

**Source materials**: 3 RFC proposals, benchmark reports, production incident postmortems, vendor documentation.

**Phase 2 prompt**:
```
What does every team that successfully runs this architecture at scale understand
that the documentation never mentions?
```

**Phase 3 prompt**:
```
What are the 3 core assumptions this architecture is built on?
For each: what would have to be true for it to become a liability at 10x scale?
```

**Phase 4 prompt**:
```
Write 5 questions a principal engineer at a FAANG company would ask
to reject this architecture proposal,
then answer each one using only evidence from these documents.
```

---

## Example 3: Competitive Intelligence

**Source materials**: competitor product pages, G2/Capterra reviews, job postings, blog posts, changelogs.

**Phase 2 prompt**:
```
What does every successful competitor in this space understand about their users
that they deliberately do NOT put in their marketing?
```

**Phase 3 prompt**:
```
What are the 3 assumptions the current market leader's strategy depends on?
What emerging signals suggest any of these might be wrong?
```

---

## Example 4: Security Threat Modeling

**Source materials**: architecture diagrams, API docs, deployment configs, past incident reports.

**Phase 2 prompt**:
```
What does every attacker who has successfully breached similar systems understand
that the defenders assume is not exploitable?
```

**Phase 4 prompt**:
```
Write 5 attack scenarios a senior red team operator would attempt
against this system, then assess the current defenses using only
the evidence in these documents.
```

---

## Anti-Pattern: What NOT to Do

Bad (no documents, vague question):
```
Analyze the SaaS market for me.
```

Bad (summarization request):
```
Summarize these competitor pages.
```

Bad (skipping phases):
```
Just give me the risks.
```

The power of this framework comes from the sequential buildup.
Phase 4 without Phase 2 and 3 produces shallow results.
