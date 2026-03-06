---
slug: coercion-resistance-and-anti-vote-buying
hub: agora
title: Coercion Resistance & Anti Vote-Buying Safeguards
summary: Designing systems so voters cannot prove how they voted.
permalink: https://www.envisioning.com/agora/coercion-resistance-and-anti-vote-buying
collection: ethics-security
trl: 4
impact: 5
investment: 4
image_url: null
---

# Coercion Resistance & Anti Vote-Buying Safeguards

## Summary

Designing systems so voters cannot prove how they voted.

## Description

The integrity of democratic systems fundamentally depends on the secrecy of the ballot—a principle that protects voters from coercion and prevents the commodification of votes through buying schemes. Traditional paper-based voting systems achieve this through physical separation: voters mark ballots in private booths and deposit them into sealed boxes, making it nearly impossible to prove to a third party how one voted. However, as democratic processes increasingly incorporate digital technologies—from electronic voting machines to internet-based systems—new vulnerabilities emerge. Digital systems can potentially generate cryptographic proofs or digital receipts that would allow voters to demonstrate their choices to coercers or vote buyers, undermining the protective anonymity that secret ballots provide. Coercion resistance and anti vote-buying safeguards represent a sophisticated set of cryptographic protocols and procedural designs specifically engineered to preserve ballot secrecy in digital environments, ensuring that voters cannot produce convincing evidence of their vote choices even if they actively wish to do so.

These safeguards operate through several complementary mechanisms. Receipt-freeness protocols ensure that while voters can verify their votes were counted, they receive no information that could serve as proof to others. Revoting designs allow voters to change their selections multiple times during a voting period, with only the final vote counting—this means any "proof" shown to a coercer could be invalidated by a subsequent secret vote. Carefully designed user interfaces and procedural constraints prevent voters from photographing or recording their selections in ways that would be convincing to third parties. Some advanced cryptographic approaches employ techniques like randomised partial checking or deniable encryption, where voters interact with systems in ways that preserve verifiability for election integrity while preventing the generation of transferable proofs. These mechanisms must balance multiple competing requirements: voters need sufficient assurance that their votes were recorded correctly, election observers require transparency for legitimacy, yet the system must deny voters the ability to prove their specific choices to external parties.

As digital democracy initiatives expand globally—from pilot programs in municipal elections to proposals for national-scale internet voting—the importance of these safeguards becomes increasingly critical. Research communities continue to refine these protocols, with ongoing work addressing challenges like smartphone-based voting where device control presents additional coercion vectors. The stakes are particularly high in contexts where vote buying remains prevalent or where vulnerable populations face systematic intimidation. Early deployments of coercion-resistant systems have appeared in organisational governance and small-scale civic processes, providing valuable insights into user experience challenges and the practical tensions between usability and security. Looking forward, these safeguards will likely become standard requirements for any legitimate digital voting system, as the democratic promise of expanded participation must be balanced against the fundamental need to protect voters from undue influence and preserve the sanctity of individual choice.
