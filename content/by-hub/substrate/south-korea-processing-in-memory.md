---
slug: south-korea__processing-in-memory
hub: substrate
title: Processing-in-Memory (PIM)
summary: SK Hynix is embedding compute logic directly inside DRAM chips, reducing
  the data movement bottleneck that wastes up to 60% of energy in conventional AI
  systems.
permalink: https://www.envisioning.com/substrate/south-korea__processing-in-memory
collection: hardware
trl: 6
impact: 3
investment: 3
image_url: https://res.cloudinary.com/envisioning/image/upload/v1774816566/substrate/technologies/30903f67-73c1-477d-9493-8f2c340118c3-google-gemini-3.1-flash-image-preview-0lcj8t.png
---

# Processing-in-Memory (PIM)

## Summary

SK Hynix is embedding compute logic directly inside DRAM chips, reducing the data movement bottleneck that wastes up to 60% of energy in conventional AI systems.

## Description

SK Hynix's AiM (Accelerator-in-Memory) technology embeds processing units within HBM and GDDR memory chips, allowing basic compute operations to happen where data already resides rather than shuttling it to a separate CPU or GPU. The first-generation AiM chips target AI inference workloads like recommendation systems and natural language processing.

The data movement problem is the dominant energy cost in modern computing — moving a byte of data from DRAM to a processor consumes 100-1000x more energy than the computation itself. PIM architectures attack this directly by putting simple multiply-accumulate units inside the memory array. Samsung has parallel PIM research (HBM-PIM), making Korea the only country with two companies simultaneously developing production-grade processing-in-memory.

PIM is unlikely to replace GPUs for large-scale AI training, but for inference at the edge and in data centers, it promises 2-5x energy efficiency improvements. As AI inference costs begin to dwarf training costs, PIM could become a critical technology for sustainable AI deployment.
