---
name: deep-analysis
description: >-
  Structured deep analysis framework using a 5-phase adversarial questioning pipeline.
  Compresses weeks of research into hours by extracting hidden consensus, inverting
  assumptions, and stress-testing conclusions. Use when the user asks to deeply analyze
  a market, strategy, technology, competitor, business idea, architecture decision,
  or any complex topic requiring rigorous multi-angle evaluation.
---

# Deep Analysis Framework

A structured 5-phase pipeline that turns raw documents into battle-tested strategic insights through progressively adversarial questioning.

## Prerequisites

Before starting, gather source materials from the user. The more concrete and first-hand the inputs, the better the output.

Good inputs: competitor pages, earnings transcripts, customer reviews, complaint threads, RFCs, architecture docs, benchmark reports, internal postmortems.

Bad inputs: no documents (forces the model to rely on training data — generic results).

If the user provides no documents, ask them to supply at least 3-5 concrete sources before proceeding.

## The 5-Phase Pipeline

Execute phases sequentially. Each phase builds on the previous output.

### Phase 1: Context Loading

Ingest all provided documents. Do NOT summarize yet. Confirm receipt:

```
I've loaded [N] documents:
1. [type]: [brief identifier]
2. [type]: [brief identifier]
...
Ready for Phase 2.
```

### Phase 2: Hidden Consensus Extraction

Ask the core insight question:

```
Based on all provided materials:

What does every successful player in this space understand
that their customers / users / stakeholders never say out loud?

List 3-5 unspoken truths, each with:
- The insight itself (one sentence)
- Evidence from the documents that supports it
- Why this stays unspoken (incentive structure)
```

This targets **tacit knowledge** — the kind that normally takes years of domain immersion to develop.

### Phase 3: Assumption Inversion

Attack the foundations:

```
What are the 3 core assumptions this entire space is built on?

For each assumption:
1. State it explicitly
2. Explain why everyone currently accepts it
3. What would have to be true for this assumption to be WRONG?
4. Is there any evidence in the documents that it might already be cracking?
```

Output = the **attack surface** of the domain. Blind spots, fragile consensus, unexploited openings.

### Phase 4: Red Team Attack

Simulate a hostile expert review:

```
Write 5 questions a world-class [domain expert / investor / critic]
would ask to DESTROY the proposed [strategy / architecture / idea].

Then answer each one using ONLY evidence from the provided documents.

Rate each answer:
- STRONG: evidence clearly supports the position
- MODERATE: evidence is partial or indirect
- WEAK: no strong evidence, relies on assumptions
```

Every WEAK or MODERATE answer becomes a follow-up target.

### Phase 5: Steelman Stress Test

For each weak point identified in Phase 4:

```
What is the STRONGEST version of this argument?
Present it as compellingly as possible.

Now: where does even this strongest version still break?
What is the irreducible risk that cannot be argued away?
```

This is **steelmanning** — strengthening the opposing argument before finding its true limits.

## Output Format

After all 5 phases, produce a synthesis:

```markdown
# Deep Analysis: [Topic]

## Executive Summary
[3-5 sentence overview of the most important findings]

## Hidden Consensus (Phase 2)
[Top 3 unspoken truths with evidence]

## Assumption Map (Phase 3)
| Assumption | Stability | Crack Evidence |
|------------|-----------|----------------|
| ...        | ...       | ...            |

## Vulnerability Assessment (Phase 4)
| Attack Vector | Defense Strength | Residual Risk |
|---------------|-----------------|---------------|
| ...           | STRONG/MOD/WEAK | ...           |

## Irreducible Risks (Phase 5)
[Risks that survive even the strongest counterarguments]

## Strategic Implications
[What to do given all of the above]
```

## Adaptation by Domain

The framework is domain-agnostic. Adjust the Phase 4 expert role:

| Domain | Expert Role |
|--------|------------|
| Market / GTM | "world-class VC investor" |
| Architecture | "principal engineer at a FAANG company" |
| Security | "senior red team operator" |
| Product | "head of product at a direct competitor" |
| Research | "hostile peer reviewer at a top-tier venue" |

## Guidelines

- Never skip phases or combine them. The sequential buildup is critical.
- Always ground answers in the provided documents. Flag when inference goes beyond the evidence.
- Prefer specificity over breadth. 3 sharp insights beat 10 vague ones.
- When a phase produces unexpected results, pause and ask the user if they want to explore that branch deeper before continuing.

## Additional Resources

- For domain-specific prompt templates, see [examples.md](examples.md)
