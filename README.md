# GeoPilot

**Ask a road a question.**

A voice-first geospatial AI co-pilot for road and urban planning in growing, under-mapped African cities.

---

## The Problem

As African cities grow, informal settlements expand faster than road networks can keep up. Streets get built informally, without planning — leaving households cut off from clinics, markets, and main roads. Congestion builds unpredictably. During floods or erosion, entire sections can lose the one access route they had.

Planners have no fast way to reason about which road or bridge would actually help, because the underlying map of what exists is incomplete or missing entirely — official GIS data is weakest exactly where the need is greatest.

## The Idea

GeoPilot lets a planner speak a question about a real location and get an answer grounded in live geospatial reasoning — no GIS software, no digging through map layers.

It combines:
- **Speech-to-text** for natural voice queries
- **An LLM** for reasoning and tool orchestration
- **Geospatial data** — satellite/aerial imagery and humanitarian OSM data, since informal settlements are where standard datasets are weakest
- **A live 3D environment** as the visual proof behind every answer

The goal isn't another voice chatbot. It's a conversation with the physical world — specifically, the parts of the city that were never fully mapped.

## The "Wow" Moment

A presenter points at an unmapped settlement in the 3D scene and asks:

> *"How many households gain access if we build a road here?"*

> *"Which part of this settlement loses its only route out if this road floods?"*

GeoPilot traces the proposed road through the 3D city and highlights, live, who it connects or cuts off.

## Key Use Cases

| Use case | What it answers |
|---|---|
| **Road gap analysis** | Which clusters of housing have no real road access today? |
| **Proposed road/bridge impact** | Who gains or loses access if we build here instead? |
| **Congestion & growth reasoning** | As a settlement grows, where will road demand break first? |
| **Flood/erosion route resilience** | Which roads are the *only* access route, and vulnerable to seasonal flooding? |
| **Growth-aware planning** | How has the informal road network grown over time, and where should formal planning step in next? |

## Tech Stack

- **3D / geospatial foundation:** built on top of Traffic Lab 3D, an open-source geospatial visualization engine (satellite imagery + 3D representations) — GeoPilot is the product layer on top, not a repackaged traffic app
- **Realtime transcription:** AssemblyAI Realtime Speech-to-Text API (WebSockets), bringing our own LLM, tools, and text-to-speech layer for full control over orchestration
- **Frontend:** React, rendered 3D wireframe city visualization (Three.js) as the interactive backdrop for the co-pilot experience

