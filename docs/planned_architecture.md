# Planned Architecture: ET Intelligence Platform (FolioPP)

This document outlines the target directory structure and architectural blueprint for the FolioPP project, defining the relationship between the Agentic Reasoning layer, the Data Pipelines, and the High-Density Frontend Terminal.

```text
et-intelligence-platform/
├── README.md
├── Makefile
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── frontend/                           # React + TypeScript Frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── public/
│   │   ├── favicon.svg
│   │   └── mock-data/
│   │       ├── patterns-sample.json
│   │       └── signals-sample.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── assets/
│       │   └── styles/globals.css
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Sidebar.tsx
│       │   │   ├── Header.tsx
│       │   │   └── Layout.tsx
│       │   ├── charts/
│       │   │   ├── CandlestickChart.tsx
│       │   │   ├── PatternOverlay.tsx
│       │   │   └── VolumeChart.tsx
│       │   ├── signals/
│       │   │   ├── SignalCard.tsx
│       │   │   └── SignalStrength.tsx
│       │   ├── patterns/
│       │   │   ├── PatternBadge.tsx
│       │   │   └── SuccessRateMeter.tsx
│       │   ├── chat/
│       │   │   ├── ChatInterface.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   └── StreamingMessage.tsx
│       │   └── shared/
│       │       ├── LoadingSpinner.tsx
│       │       └── ErrorBoundary.tsx
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── OpportunityRadar.tsx
│       │   ├── ChartIntelligence.tsx
│       │   ├── MarketChat.tsx
│       │   └── Portfolio.tsx
│       ├── hooks/
│       │   ├── useStockData.ts
│       │   ├── usePatterns.ts
│       │   ├── useSignals.ts
│       │   └── useChat.ts
│       ├── services/
│       │   ├── api-client.ts
│       │   └── websocket.ts
│       ├── store/
│       │   ├── userStore.ts
│       │   └── portfolioStore.ts
│       ├── types/
│       │   ├── stock.ts
│       │   ├── patterns.ts
│       │   └── signals.ts
│       └── utils/
│           ├── formatters.ts
│           └── chartHelpers.ts
│
├── backend/                            # FastAPI Backend
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   │
│   ├── agents/                         # LangGraph Agents
│   │   ├── __init__.py
│   │   ├── state.py
│   │   ├── graph.py
│   │   └── nodes/
│   │       ├── planner.py              # Intent detection
│   │       ├── retriever.py             # Parallel data fetch
│   │       ├── analyst.py                # Pattern/signal analysis
│   │       ├── portfolio_context.py       # User holdings
│   │       └── responder.py                # Answer generation
│   │
│   ├── clients/                         # Async DB Clients
│   │   ├── ray_llm.py
│   │   ├── ray_embed.py
│   │   ├── qdrant.py
│   │   ├── neo4j.py
│   │   ├── redis.py
│   │   └── postgres.py
│   │
│   ├── signals/                         # Opportunity Radar
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── scanners/
│   │   │   ├── filing_changes.py
│   │   │   ├── bulk_deals.py
│   │   │   ├── insider_trades.py
│   │   │   ├── management_changes.py
│   │   │   └── regulatory_updates.py
│   │   ├── scorers/
│   │   │   ├── signal_score.py
│   │   │   └── confidence.py
│   │   └── alerts/
│   │       └── generator.py
│   │
│   ├── patterns/                        # Chart Intelligence
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── technical/
│   │   │   ├── candlestick.py
│   │   │   ├── support_resistance.py
│   │   │   ├── divergences.py
│   │   │   └── breakouts.py
│   │   ├── backtester/
│   │   │   ├── historical.py
│   │   │   └── success_rate.py
│   │   └── explainer/
│   │       └── plain_english.py
│   │
│   ├── rag/                             # RAG Components
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retrievers/
│   │       ├── semantic.py
│   │       └── hybrid.py
│   │
│   ├── cache/                           # Semantic Caching
│   │   └── semantic.py
│   │
│   ├── memory/                          # Conversation Memory
│   │   ├── models.py
│   │   └── postgres.py
│   │
│   ├── enhancers/                       # Query Enhancement
│   │   ├── query_rewriter.py
│   │   └── hyde.py
│   │
│   ├── routes/                          # API Endpoints
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── signals.py
│   │   ├── patterns.py
│   │   ├── portfolio.py
│   │   ├── stocks.py
│   │   └── health.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── timing.py
│       └── retry.py
│
├── pipelines/                           # Ray Data Pipelines
│   ├── ingestion/
│   │   ├── config.yaml
│   │   ├── loaders/
│   │   │   ├── nse_filings.py
│   │   │   ├── price_history.py
│   │   │   └── news.py
│   │   ├── chunking/
│   │   │   ├── splitter.py
│   │   │   └── metadata.py
│   │   ├── embedding/
│   │   │   └── compute.py
│   │   ├── graph/
│   │   │   ├── schema.py
│   │   │   └── extractor.py
│   │   └── indexing/
│   │       ├── qdrant_indexer.py
│   │       └── neo4j_indexer.py
│   └── jobs/
│       ├── daily_signal_generation.py
│       └── pattern_backtesting.py
│
├── models/                              # Model Configs
│   ├── llm/
│   │   ├── mistral-7b.yaml
│   │   └── llama-70b.yaml
│   ├── embeddings/
│   │   └── bge-m3.yaml
│   └── patterns/
│       └── config.yaml
│
├── libs/                                # Shared Libraries
│   ├── schemas/
│   │   ├── patterns.py
│   │   ├── signals.py
│   │   └── chat.py
│   ├── observability/
│   │   ├── metrics.py
│   │   ├── tracing.py
│   │   └── logging.py
│   └── utils/
│       ├── ids.py
│       └── validators.py
│
├── infra/                               # Infrastructure as Code
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── vpc.tf
│   │   ├── eks.tf
│   │   ├── rds.tf
│   │   └── outputs.tf
│   └── karpenter/
│       ├── provisioner-cpu.yaml
│       └── provisioner-gpu.yaml
│
├── deploy/                              # Kubernetes Manifests
│   ├── helm/
│   │   ├── qdrant/
│   │   │   └── values.yaml
│   │   ├── neo4j/
│   │   │   └── values.yaml
│   │   └── redis/
│   │       └── values.yaml
│   ├── ray/
│   │   ├── ray-cluster.yaml
│   │   ├── ray-serve-patterns.yaml
│   │   ├── ray-serve-signals.yaml
│   │   └── autoscaling.yaml
│   └── ingress/
│       └── nginx.yaml
│
├── scripts/                             # Utility Scripts
│   ├── bootstrap_cluster.sh
│   ├── cleanup.sh
│   ├── load_test.py
│   ├── warmup_cache.py
│   ├── seed_database.py
│   └── download_nse_data.py
│
├── tests/                               # Tests
│   ├── test_patterns.py
│   ├── test_signals.py
│   ├── test_agents.py
│   └── test_api.py
│
├── eval/                                # Evaluation
│   ├── datasets/
│   │   └── golden.json
│   ├── judges/
│   │   └── llm_judge.py
│   └── reports/
│
├── notebooks/                           # Development
│   ├── 01_pattern_backtesting.ipynb
│   ├── 02_signal_generation.ipynb
│   └── 03_agent_evaluation.ipynb
│
└── demo/                                # Pitch Materials
    ├── architecture_diagram.png
    ├── sample_alerts.json
    ├── sample_patterns.json
    └── pitch_deck.pptx
```
