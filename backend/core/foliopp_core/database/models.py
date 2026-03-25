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
