from sqlalchemy import Column, DateTime, Integer, String, func, Float, BigInteger, or_
from sqlalchemy.sql.expression import label, cast
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

from . import engine, session


Base = declarative_base()


class PaymentEvent(Base):
    __tablename__ = "paymentevent"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False, default=0)
    currency = Column(String(16), nullable=False)
    _metadata = Column(String(100), nullable=False)
    sender = Column(String(100))
    recipient = Column(String(100))
    type = Column(String(100), nullable=False)
    transactionkey = Column(String(100))
    seq = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AccountTransaction(Base):
    __tablename__ = "accounttransaction"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False)
    tx = Column(JSONB, nullable=False)
    hash = Column(String(64), nullable=False)
    vm_status = Column(JSONB)
    gas_used = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AccountBalance(Base):
    __tablename__ = "accountbalance"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False)
    account_type = Column(String(100), nullable=False)
    balance = Column(BigInteger, nullable=False)
    wallet_type = Column(String(1), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ALTER TABLE accountbalance ADD COLUMN wallet_type CHAR(1);

# uncomment to have db created here:
# if engine:
#     Base.metadata.create_all(engine)
