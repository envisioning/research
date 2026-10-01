---
slug: gaussian-splatting-engines-3d
hub: prism
title: 3D Gaussian Splatting Engines
summary: Real-time rendering of photorealistic 3D scenes from multi-view photos using
  GPU-rasterized Gaussian splats
permalink: https://www.envisioning.com/prism/gaussian-splatting-engines-3d
collection: software
trl: 5
impact: 4
investment: 3
image_url: https://res.cloudinary.com/envisioning/image/upload/v1764074562/pulse/technologies/gaussian-splatting-engines-3d-gemini-3-pro-z6wqvk.jpg
updated_at: '2026-05-25T12:53:52.153719+00:00'
last_reviewed: null
---

# 3D Gaussian Splatting Engines

## Summary

Real-time rendering of photorealistic 3D scenes from multi-view photos using GPU-rasterized Gaussian splats

## Description

3D Gaussian splatting engines represent scenes as millions of anisotropic Gaussian blobs with per-blob color, opacity, and covariance. Instead of ray marching through neural networks, they rasterize these splats directly on the GPU, achieving NeRF-level realism at interactive frame rates and allowing editors to edit splats like particles. Capture pipelines convert multi-view images into splat clouds in minutes, enabling portable files that stream efficiently to WebGL, Unreal, or custom viewers.

Studios use splats to build volumetric location libraries for AR scouting, lightweight digital twins for sports replays, and immersive tourism experiences that run on phones. Because the format supports progressive refinement, streaming services can send low-res previews first, then layer in detail as bandwidth allows. Paired with LiDAR data, splats fill gaps with photoreal draw-ins, helping virtual production teams align CG and practical sets.

Ecosystem maturity (TRL 5) hinges on tooling: DCC apps need splat-aware editing, and compression standards must emerge to keep files manageable. Open-source viewers from Graphdeco and Luma Labs demonstrate what’s possible, and standards bodies discuss adding splat modes to glTF. Expect Gaussian splatting to sit alongside NeRFs as a pragmatic option where real-time playback and editability trump absolute compression rates.
