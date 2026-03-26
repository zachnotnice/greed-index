from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Billionaire(Base):
    __tablename__ = "billionaires"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    net_worth_billions = Column(Float, nullable=False)  # in USD billions
    industry = Column(String, nullable=False)
    wealth_source = Column(String, nullable=False)  # e.g. "Tesla, SpaceX"
    company = Column(String)
    photo_url = Column(String)
    twitter_handle = Column(String)
    wikipedia_url = Column(String)
    birth_year = Column(Integer)
    giving_pledge_signed = Column(Boolean, default=False)
    giving_pledge_fulfilled = Column(Boolean, default=False)  # have they actually given?
    bio_blurb = Column(Text)

    # Annual wealth growth rate (%) — used in greed scoring
    annual_wealth_growth_pct = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    donations = relationship("Donation", back_populates="billionaire", cascade="all, delete-orphan")
    greed_scores = relationship("GreedScore", back_populates="billionaire", cascade="all, delete-orphan")
    wealth_snapshots = relationship("WealthSnapshot", back_populates="billionaire", cascade="all, delete-orphan")

    @property
    def latest_greed_score(self):
        if self.greed_scores:
            return sorted(self.greed_scores, key=lambda x: x.calculated_at, reverse=True)[0]
        return None


class GreedScore(Base):
    __tablename__ = "greed_scores"

    id = Column(Integer, primary_key=True, index=True)
    billionaire_id = Column(Integer, ForeignKey("billionaires.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)           # 0-100, higher = greedier
    rank = Column(Integer)                           # 1 = greediest
    adjusted_giving_billions = Column(Float)         # giving after loophole deductions
    total_giving_claimed_billions = Column(Float)    # what they claim to give
    loophole_amount_billions = Column(Float)         # amount classified as loopholes
    giving_ratio_pct = Column(Float)                 # adjusted_giving / net_worth * 100
    wealth_penalty = Column(Float)                   # penalty for wealth growing faster than giving
    quality_score = Column(Float)                    # 0-1, quality of giving mechanisms
    score_breakdown = Column(JSON)                   # detailed breakdown for transparency
    calculated_at = Column(DateTime, default=datetime.utcnow)

    billionaire = relationship("Billionaire", back_populates="greed_scores")


class WealthSnapshot(Base):
    __tablename__ = "wealth_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    billionaire_id = Column(Integer, ForeignKey("billionaires.id"), nullable=False, index=True)
    net_worth_billions = Column(Float, nullable=False)
    snapshot_date = Column(DateTime, default=datetime.utcnow)
    source = Column(String)

    billionaire = relationship("Billionaire", back_populates="wealth_snapshots")
