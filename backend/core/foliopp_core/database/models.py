from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from backend.clients.postgres import Base

class IngestedBatch(Base):
    __tablename__ = "ingested_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True)  # nse, yfinance
    fetcher_name = Column(String, index=True) # NSEDeliverableFetcher
    query_params = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_storage_uri = Column(String)  # minio path
    entry_count = Column(Integer)
    processed = Column(Boolean, default=False)

class BulkDeal(Base):
    __tablename__ = "bulk_deals"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("ingested_batches.id"))
    trade_date = Column(DateTime, index=True)
    symbol = Column(String, index=True)
    client_name = Column(String)
    deal_type = Column(String) # SELL, BUY
    quantity = Column(Integer)
    price = Column(Float)
    is_promoter = Column(Boolean, default=False)
    pct_equity = Column(Float) 
    priority = Column(Integer, default=0) # 1 for high priority
    raw_metadata = Column(JSON)

class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("ingested_batches.id"))
    symbol = Column(String, index=True)
    entity_type = Column(String)  # Filing, Price, CorporateAction
    vector_id = Column(String)    # Qdrant point id
    graph_id = Column(String)     # Neo4j node id
    last_updated = Column(DateTime, default=datetime.utcnow)

class PortfolioEntry(Base):
    __tablename__ = "portfolio_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    units = Column(Integer)
    avg_price = Column(Float)
    sector = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

class NSETicker(Base):
    __tablename__ = "nse_tickers"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, unique=True)
    name = Column(String)
    sector = Column(String)
    market_cap = Column(Float, nullable=True)
    market_cap_bucket = Column(String, nullable=True) # Large Cap, Mid Cap, Small Cap

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)  # user, assistant
    content = Column(String, nullable=False)
    thoughts = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
