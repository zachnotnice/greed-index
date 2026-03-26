from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class DonationType(str, enum.Enum):
    DIRECT_GRANT = "direct_grant"           # direct cash to operating charity ✓
    FOUNDATION = "foundation"               # to their own private foundation (may be ok)
    DAF = "donor_advised_fund"              # donor-advised fund (often loophole)
    CHARITABLE_LLC = "charitable_llc"       # LLC structure, no transparency ✗
    CONSERVATION_EASEMENT = "conservation_easement"  # personal property tax dodge ✗
    NAMING_RIGHTS = "naming_rights"         # vanity donation to get a building named ✗
    POLITICAL = "political"                 # political "charity" / issue advocacy ✗
    GIVING_PLEDGE = "giving_pledge"         # pledge (not yet given)
    IN_KIND = "in_kind"                     # non-cash assets
    IMPACT_INVESTMENT = "impact_investment" # retained-control "giving"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    ein = Column(String, unique=True)           # IRS EIN for 990 lookup
    cause_category = Column(String)             # health, education, poverty, environment, arts, etc.
    overhead_ratio_pct = Column(Float)          # admin overhead as % of expenses
    payout_ratio_pct = Column(Float)            # % of assets paid out annually
    is_transparent = Column(Boolean, default=True)
    watchdog_rating = Column(String)            # Charity Navigator rating
    notes = Column(Text)

    donations = relationship("Donation", back_populates="organization")


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    billionaire_id = Column(Integer, ForeignKey("billionaires.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization_name = Column(String, nullable=False)
    amount_billions = Column(Float, nullable=False)
    year = Column(Integer)
    donation_type = Column(String, default=DonationType.DIRECT_GRANT)

    # Loophole classification
    is_loophole = Column(Boolean, default=False)
    loophole_reason = Column(Text)
    loophole_pct = Column(Float, default=0.0)   # 0-1, what fraction is "loophole"

    # Metadata
    source_url = Column(String)
    notes = Column(Text)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    billionaire = relationship("Billionaire", back_populates="donations")
    organization = relationship("Organization", back_populates="donations")
