# FolioPP

The Reasoning Layer for Modern Financial Markets.

Bridging the gap between high-frequency signal arrival and logical market action for Indian retail investors.

---

## 🚀 Quick Start (Docker)

The easiest way to get started is using Docker and the provided `Makefile`.

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FolioPP
   ```

2. **Run the development environment**
   ```bash
   make dev
   ```
   This will start all required services (Qdrant, Neo4j, Redis, etc.) and launch the backend and frontend.

   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)

---

## 🛠 Manual Setup

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** (pnpm recommended)
- **Docker & Docker Compose** (for infrastructure)

### 2. Infrastructure Setup
FolioPP relies on several databases and middleware. Start them using Docker:
```bash
docker-compose up -d
```

### 3. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows: venv\Scripts\activate
   # On Linux/macOS: source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the server:
   ```bash
   python main.py
   ```

### 4. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install # or pnpm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

---

## 📖 Available Commands

| Command | Description |
| :--- | :--- |
| `make install` | Install all backend and frontend dependencies |
| `make dev` | Start infrastructure and show service URLs |
| `make up` | Start Docker containers and seed database |
| `make down` | Stop all Docker containers |
| `make test` | Run backend (pytest) and frontend tests |
| `make clean` | Stop containers and remove volumes |

---
*Visit the [Documentation](https://foliopp.docs) for architectural details.*
