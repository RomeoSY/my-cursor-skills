---
name: deep-analysis
version: 1.2.0
description: >-
  Structured 5-phase adversarial analysis: hidden consensus, assumption inversion, stress tests.
  Triggers: deep analysis, 深度分析, 战略分析, architecture review, market strategy.
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

After all 5 phases, produce a synthesis. **Use the Chinese template below for user-facing headings and tables** (keep English terms in parentheses where needed for clarity).

```markdown
# 深度分析：[主题]

## 执行摘要（Executive Summary）
[3–5 句概括最重要结论]

## 隐性共识（阶段 2）
[附证据的前 3 条「行业共识但未明说」]

## 假设图谱（阶段 3）
| 假设 | 稳定性 | 出现裂缝的证据 |
|------|--------|----------------|
| ...  | ...    | ...            |

## 脆弱性评估（阶段 4）
| 攻击向量 | 防御强度 | 残余风险 |
|----------|----------|----------|
| ...      | 强/中/弱（STRONG/MOD/WEAK） | ... |

## 不可消解风险（阶段 5）
[即使最强反驳仍存在的风险]

## 战略启示
[综合以上应采取的立场与行动]
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
