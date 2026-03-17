# The Solution (Planned)

## What We're Actually Building

Imagine having a brilliant research analyst working 24/7 just for you—someone who reads every company filing, watches every insider trade, scans every chart, and knows your portfolio inside out. Every morning, they send you a short message: "Here are 3 things you missed that actually matter for your money."

That's what we're building.


## The Three Things We Do

### 1. Opportunity Radar: What Did You Miss?

**The Problem:** Every day, hundreds of companies file results, insiders buy or sell, and regulations change. You can't read it all. So you miss things.

**Our Solution:** An AI that reads everything—every filing, every result, every insider trade, every regulatory update across the entire stock market. It doesn't just tell you *something happened*. It tells you when *something changed* that matters.

**Example:**
> Instead of: "Reliance released quarterly results"
> 
> We tell you: "Reliance just reported accelerating growth for the third quarter in a row, insiders bought for the first time in two years, and management sounds more confident than usual. The last time this combination happened, the stock gained 18% over the next 6 months."

That's not a summary. That's a **signal**.

### 2. Chart Pattern Intelligence: What Is the Chart Telling You?

**The Problem:** You see a chart with lines and candles. Maybe it looks like a pattern. But what does it *mean*? And does it even work for *this* stock?

**Our Solution:** We scan every stock in real-time, looking for technical patterns. When we find one, we don't just show you the pattern. We tell you: "This exact pattern has appeared on this exact stock 23 times before. Here's what happened next."

**Example:**
> Instead of: "Bullish flag detected on TCS"
> 
> We tell you: "TCS is showing a bullish flag pattern. This pattern has appeared on TCS 18 times in the last 8 years. 14 times it led to higher prices within 30 days—that's a 78% success rate. The average gain was 8.3%. Based on history, there's a good chance TCS goes up another 8% over the next 2 weeks."

That's not guesswork. That's **probability based on history**.

### 3. Portfolio-Aware Intelligence: What Does This Mean for *You*?

**The Problem:** News happens. Markets move. But most of it doesn't matter for your specific portfolio. Figuring out what *does* matter takes work.

**Our Solution:** We know what you own. So when something happens, we filter out the noise and tell you only what affects your money—and how.

**Example:**
> Instead of: "RBI tightens lending norms"
> 
> We tell you: "RBI just tightened lending norms. This affects HDFC Bank, which is 40% of your portfolio. The last time this happened, HDFC underperformed for 3 months before recovering. You might consider hedging or holding through the volatility—here's what history suggests."

That's not generic news. That's **personalized intelligence**.


## How It's Different from What Exists Today

| Today's Tools | What We Build |
|--------|---------|
| News aggregators that show you everything | Signal finders that show you only what matters |
| Charting tools that highlight patterns | Pattern intelligence with stock-specific history |
| Portfolio trackers that show performance | Portfolio intelligence that shows *what affects* your performance |
| Alerts for every event | Alerts only when something *changed* |
| Jargon-filled analysis | Plain English explanations |
| Generic advice | Personalized to your holdings |


## In Simple Terms

Most investors today have access to the same information as professionals. What they don't have is the **time** or the **training** to make sense of it all.

We're building the brain that does the hard work for you.

You don't need to read 100-page filings. We read them.
You don't need to memorize chart patterns. We detect them.
You don't need to connect dots across different news. We connect them.
You don't need to calculate how events affect your portfolio. We calculate it.

**Every morning, you get a short, clear message:**
- "Here are 3 opportunities you might have missed"
- "Here's what changed overnight that matters for your money"
- "Here's what the charts are saying about stocks you care about"

No noise. No jargon. Just **actionable intelligence**.


## The Bigger Picture

India has 14 crore demat accounts. Most of those investors are smart people who want to make good decisions. They're not losing money because they're stupid. They're losing money because the system gives them raw data but no help understanding it.

We're building the help.

Not a chatbot that answers questions. Not a news feed. Not a charting tool.

**A reasoning layer** that turns the firehose of market information into clear, simple, money-making decisions.

That's it. That's what we're building.


*Now, for the technical readers, here's how we actually build this at scale...*


# System Architecture

## 1. Architectural Overview

Building on the production-grade principles from the blog, our platform is structured as a **six-layer intelligence stack** designed specifically for Indian market data at scale. Each layer has a clear responsibility, and together they transform raw market information into actionable signals for retail investors.

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                             │
│  Corporate  │  Regulatory  │  Market  │  News  │  Social     │
│  Filings    │  Disclosures │  Data    │  Feeds │  Media      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                     │
│      Ray Data Pipelines | Loaders | Chunking | Indexing      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Qdrant  │ │  Neo4j   │ │PostgreSQL│ │  Redis   │       │
│  │ (Vector) │ │ (Graph)  │ │ (Users)  │ │ (Cache)  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                    ┌──────────────┐                          │
│                    │  S3 / MinIO  │                          │
│                    │ (Raw Files)  │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      COMPUTE LAYER                            │
│    ┌─────────────────┐    ┌─────────────────┐               │
│    │ Pattern Engine  │    │   LLM Serving   │               │
│    │  (Ray Actors)   │    │ (LLM Models)    │               │
│    └─────────────────┘    └─────────────────┘               │
│    ┌─────────────────┐    ┌─────────────────┐               │
│    │  Embeddings     │    │  Re-ranking     │               │
│    │  (BGE-M3)       │    │  (Cross-encoder)│               │
│    └─────────────────┘    └─────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AGENTIC ORCHESTRATION LAYER                │
│         LangGraph Agents: Planner → Retriever → Analyst      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        API GATEWAY                           │
│              FastAPI | Rate Limiting | Auth                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                      │
│         React Frontend | Mobile App | Alert System           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Layer 1: Data Sources & Acquisition

### 2.1 Data Sources We Need

| Source | Data Type | Why It Matters |
|--------|-----------|----------------|
| **Corporate Filings** | Quarterly results, annual reports, board meetings | Financial health, management outlook |
| **Regulatory Disclosures** | Insider trades, promoter holdings, pledge changes | Sentiment of those closest to the company |
| **Market Data** | Price/volume, bulk deals, block deals | What institutions are doing |
| **News Feeds** | Company news, sector news, economic news | Market-moving information |
| **Social Media** | Sentiment, emerging trends | Retail sentiment indicator |

### 2.2 Data Acquisition Approach

We don't assume we can scrape everything. We build for **multiple acquisition methods**:

**Method 1: Official Sources (when available)**
- Some exchanges provide APIs or data feeds
- Some regulators provide bulk download options
- We use these when they exist

**Method 2: Structured Web Scraping**
- For sources without APIs
- Respectful crawling with rate limiting
- Fallback mechanisms when structure changes

**Method 3: Partnerships**
- Long-term, we partner with data providers
- For MVP, we use what's publicly accessible

**Method 4: User-Contributed Data**
- Users can upload documents they find
- Community-sourced filings (with verification)

### 2.3 Acquisition Architecture

```
Scheduled Jobs (cron)
    ↓
Check for New Data
    ├─► If new filing → Download
    ├─► If price update → Fetch
    └─► If news → Pull from RSS/API
    ↓
Store Raw Data in S3
    ↓
Trigger Processing Pipeline
```

**Key Principles:**
- **Idempotent processing** - Same file processed once
- **Content hashing** for deduplication
- **Dead letter queues** for failed files
- **Backfill capability** for historical data
- **Graceful degradation** when sources unavailable

---

## 3. Layer 2: Data Ingestion Layer

### 3.1 Distributed Processing with Ray Data

Following the blog, we use **Ray Data** for parallel processing:

```
Raw Files in S3
    ↓
Ray Data reads files in parallel
    ↓
Parse each file based on type (PDF, HTML, etc.)
    ↓
Chunk text with overlap (preserve context)
    ↓
Two parallel paths:
    ├─► Generate embeddings (semantic understanding)
    └─► Extract entities and relationships (graph)
    ↓
Store in respective databases
```

### 3.2 Document Processing

**For Each Document Type:**

| Document Type | Processing Approach | Challenges |
|---------------|---------------------|------------|
| **PDF Filings** | Extract text + tables; preserve structure | Scanned docs, complex tables |
| **HTML Pages** | Strip markup; extract main content | Navigation, ads, inconsistent structure |
| **Structured Data** | Parse CSV/JSON; validate | Schema changes over time |
| **Images/Scans** | OCR when needed; fallback to manual | Low quality, handwriting |

### 3.3 Chunking Strategy

We chunk text for two reasons:
1. **Embedding limits** - Models have maximum input size
2. **Retrieval precision** - Smaller chunks = more precise matches

**Approach:**
- Split on semantic boundaries (paragraphs, sections)
- Maintain overlap to preserve context
- Preserve document structure where possible
- Keep financial tables intact (don't split across rows)

Each chunk retains:
- Source document metadata
- Position in document (for reconstruction)
- Section type (financials, commentary, risks)

### 3.4 Storage Strategy

We use multiple storage systems because no single database does everything well:

| Storage | Purpose | Why This Choice |
|--------|---------|-----------------|
| **Vector DB (Qdrant)** | Semantic search across all documents | Find similar content by meaning, not just keywords |
| **Graph DB (Neo4j)** | Entity relationships (companies, people, events) | Answer "who is connected to whom" questions |
| **Relational DB (PostgreSQL)** | User data, portfolios, chat history | Structured data with transactions |
| **Cache (Redis)** | Fast access to patterns, rate limiting | Sub-millisecond latency |
| **Object Storage (S3)** | Raw files, large documents | Cost-effective, durable |

---

## 4. Layer 3: Compute Layer

### 4.1 Model Serving Architecture

Following the blog, we **decouple models from the API**:

```
API Request
    ↓
Ray Serve Router
    ↓
Model Replica (auto-scaling)
    ↓
Response
```

Benefits:
- Models scale independently based on load
- Can update models without restarting API
- Share GPU resources across models
- Handle spiky traffic patterns

### 4.2 Models We Need

| Model | Purpose | Why |
|-------|---------|-----|
| **LLM (Mistral-7B or similar)** | Generate explanations, detect signals, answer questions | Small enough to run on one GPU, capable enough for financial text |
| **Embedding Model (BGE-M3)** | Convert text to vectors for search | Good with financial/technical language, multilingual |
| **Reranker Model** | Improve search quality | Second-pass filtering for precision |
| **Pattern Detection (Custom)** | Identify technical patterns | Purpose-built, runs on CPU |

### 4.3 Pattern Detection Engine

This is custom-built for our use case:

```
Price Data
    ↓
Distribute across Ray actors
    ├── Actor 1: Stocks A-G → Run pattern detectors
    ├── Actor 2: Stocks H-M → Run pattern detectors
    └── Actor 3: Stocks N-Z → Run pattern detectors
    ↓
Collect results
    ↓
Query historical database
    ↓
Enrich with stock-specific stats
    ↓
Cache for fast access
```

**Patterns We Detect:**
- Candlestick patterns (head & shoulders, double top/bottom, engulfing)
- Support and resistance levels
- Trendline breakouts
- Momentum divergences (RSI, MACD)
- Volume patterns

### 4.4 Performance Considerations

- **Batching** - Process multiple items together
- **Caching** - Store results to avoid recomputation
- **Pre-computation** - Run expensive jobs offline
- **Graceful degradation** - Fall back to simpler methods under load

---

## 5. Layer 4: Agentic Orchestration Layer

### 5.1 Why Agents?

A single LLM call isn't enough. We need:
- **Multi-step reasoning** - Connect dots across multiple sources
- **Tool use** - Query databases, run calculations
- **State management** - Remember conversation context
- **Planning** - Decide what to do next

### 5.2 LangGraph Agent Architecture

Following the blog, we implement a **state machine**:

```
User Input
    ↓
PLANNER: What does user want?
    ├─► "Show opportunities" → Signal Path
    ├─► "What's this chart?" → Pattern Path
    ├─► "How's my portfolio?" → Portfolio Path
    └─► General question → Q&A Path
    ↓
RETRIEVER: Get relevant data (parallel)
    ├─► Vector search (semantic)
    ├─► Graph query (relationships)
    ├─► Pattern lookup
    └─► Portfolio lookup
    ↓
ANALYST: Make sense of it all
    ├─► Detect changes vs historical
    ├─► Correlate multiple signals
    └─► Score confidence
    ↓
RESPONDER: Generate answer
    ├─► Plain English explanation
    ├─► Cite sources
    └─► Suggest actions
```

### 5.3 Agent Capabilities

**Planner**
- Understands user intent
- Routes to appropriate workflow
- Refines vague queries

**Retriever**
- Parallel searches across all data sources
- Merges and deduplicates results
- Ranks by relevance

**Analyst (Signal Detector)**
- Compares current vs historical patterns
- Identifies what changed
- Correlates across data types
- Assigns confidence scores

**Analyst (Pattern Interpreter)**
- Identifies technical patterns
- Queries historical performance
- Calculates stock-specific stats
- Generates probability context

**Portrait Context**
- Filters by user holdings
- Calculates position impact
- Personalizes insights

**Responder**
- Synthesizes findings
- Generates clear explanation
- Adds citations
- Suggests next steps

### 5.4 Query Understanding

We enhance user queries for better results:

**Query Rewriting:**
- Resolves "it", "they", "this stock"
- Creates standalone search query
- Example: "How's it doing?" → "How is Reliance Industries doing?"

**Query Expansion:**
- Adds relevant synonyms
- Includes related terms
- Improves recall

---

## 6. Layer 5: API Gateway & Presentation

### 6.1 API Layer

Built with FastAPI for high performance:

**Key Endpoints:**
- Chat interface (streaming responses)
- Daily signals digest
- Pattern queries by stock
- Portfolio analysis
- User feedback

**Features:**
- Rate limiting per user
- JWT authentication
- Request validation
- Response caching
- Graceful degradation

### 6.2 Frontend

React-based application with:

**Dashboard View:**
- Today's top signals
- Portfolio snapshot
- Recent patterns detected
- Quick chat input

**Opportunity Radar Page:**
- List of signals with strength indicators
- Filter by sector, signal type
- Historical context for each

**Chart Intelligence Page:**
- Interactive candlestick charts
- Pattern overlay
- Historical stats panel
- Plain English explanation

**Portfolio Page:**
- Holdings with current context
- Impact analysis
- Action suggestions

**Chat Interface:**
- Streaming responses
- Source citations
- Follow-up questions

### 6.3 Alert Delivery

Multi-channel to meet users where they are:

- **In-app notifications** (real-time)
- **Email digest** (daily morning)
- **Push notifications** (mobile)
- **Optional Telegram/WhatsApp** (user preference)

---

## 7. Layer 6: Infrastructure & Operations

### 7.1 Infrastructure as Code

Following the blog, we define everything in code:

**Terraform manages:**
- Network (VPC, subnets, security groups)
- Kubernetes cluster (EKS)
- Databases (Aurora, ElastiCache)
- Storage (S3 buckets)
- Permissions (IAM roles)

**Benefits:**
- Reproducible environments
- Version-controlled infrastructure
- Disaster recovery
- Audit trail

### 7.2 Kubernetes Deployment

**Helm charts for:**
- Qdrant (vector database)
- Neo4j (graph database)
- Ray cluster (compute)
- API service
- Frontend static files

**Benefits:**
- Consistent deployments
- Easy rollbacks
- Environment parity

### 7.3 Autoscaling

We scale based on actual demand, not guesses:

**CPU Workloads (Pattern Detection):**
- Scale when queue builds up
- Use spot instances when possible
- Consolidate to pack efficiently

**GPU Workloads (Model Serving):**
- Scale based on request queue
- Scale to zero when idle
- Fast spin-up for new requests

### 7.4 Observability

We can't improve what we can't measure:

**Metrics (Prometheus):**
- Request latency and error rates
- GPU utilization
- Queue lengths
- Cache hit rates
- Token usage (cost tracking)

**Tracing (OpenTelemetry):**
- End-to-end request flow
- Database query performance
- Model inference time
- Agent node duration

**Logging (Structured JSON):**
- Request IDs for correlation
- Error context
- User feedback
- Signal generation events

### 7.5 Evaluation

We continuously measure quality:

**Golden Dataset:**
- Curated question-answer pairs
- Covers all capabilities
- Updated as we learn

**Automated Metrics:**
- Faithfulness (no hallucinations)
- Answer relevance
- Signal accuracy
- Pattern detection precision

**CI/CD Gates:**
- Don't deploy if quality drops
- Catch regressions early
- A/B test improvements

---

## 8. How Requests Flow Through the System

### 8.1 Daily Signal Generation

```
1. New filings arrive throughout day
2. Each filing processed through ingestion pipeline
3. Signal detection runs on new content
4. Compare with historical patterns
5. If significant change detected:
   - Score signal strength
   - Match with relevant users
   - Store in database
6. Next morning:
   - Compile user-specific digest
   - Send email/in-app notification
```

### 8.2 Real-Time Pattern Detection

```
1. Price updates arrive (stream or poll)
2. Distribute across Ray actors by stock
3. Each actor runs pattern detectors
4. If pattern detected:
   - Query historical database
   - Calculate stock-specific stats
   - Cache result
5. If user watches this stock:
   - Generate explanation
   - Send notification
```

### 8.3 User Chat Query

```
1. User asks question
2. Rate limit check
3. Authentication
4. Planner determines intent
5. Retriever fetches data (parallel)
6. Analyst synthesizes
7. Portfolio context applied
8. Responder generates answer
9. Stream response to user
10. Log for improvement
```

---

## 9. Development Workflow

### 9.1 Local Development

```
Start local environment
    ↓
Run sample data ingestion
    ↓
Start frontend dev server
    ↓
Start backend dev server
    ↓
Test end-to-end
```

### 9.2 CI/CD Pipeline

```
Push code
    ↓
Run tests
    ↓
Build containers
    ↓
Deploy to staging
    ↓
Run evaluation suite
    ↓
If passes → deploy to production
    ↓
Monitor
    ↓
Rollback if issues
```

### 9.3 Monitoring & Alerts

- **Critical issues** → Pager/phone call
- **Warnings** → Slack/team chat
- **Daily reports** → Email
- **Dashboards** → Always available

---

## 10. Security Considerations

### 10.1 Network Security

- Databases in private subnets (no internet access)
- API only exposed through load balancer
- Security groups with least privilege
- Network policies between pods

### 10.2 Authentication & Authorization

- JWT for API access
- Rate limiting per user
- Role-based access (free vs premium)
- API keys for programmatic access

### 10.3 Data Security

- Encryption at rest (all databases, storage)
- Encryption in transit (TLS everywhere)
- Secrets in secure storage (not code)
- No sensitive data in logs

### 10.4 Compliance

- Follow SEBI guidelines for market data
- GDPR/Data privacy compliance
- Regular security reviews
- Penetration testing

---

## 11. Summary

This architecture gives us:

1. **Scalability** to handle market-wide coverage
2. **Cost efficiency** through intelligent scaling
3. **Intelligence** via agentic workflows
4. **Reliability** with proper observability
5. **Security** following best practices
6. **Maintainability** through infrastructure as code

We're applying the blog's production-grade principles to a focused domain: transforming Indian market data into actionable signals for retail investors.

The key difference from the blog is our **specialization**—we're not building a general RAG system. We're building a financial reasoning engine that understands filings, patterns, and portfolios.

---

*"Access to information is not intelligence. Synthesis is."*