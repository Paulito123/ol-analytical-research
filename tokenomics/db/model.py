import os
import re
from sqlalchemy import Column, DateTime, Integer, String, func, Float, BigInteger, or_, LargeBinary
from sqlalchemy.sql.expression import label, cast
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from typing import List, AnyStr, Dict
from datetime import datetime

from . import engine, session
# from ol_util import lookup_unlocked


Base = declarative_base()


class AccountBalance(Base):
    __tablename__ = "accountbalance"

    id = Column(Integer, primary_key=True)
    address = Column(String(100), nullable=False, unique=True)
    account_type = Column(String(100), nullable=False)
    balance = Column(BigInteger, nullable=False)
    unlocked = Column(BigInteger, nullable=True)
    wallet_type = Column(String(1), nullable=False, default='X')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def lookup_wallet_type(address: AnyStr) -> AnyStr:
        """
        Checks if a given address is a slow wallet.
        :param address: the address to check
        :return: 'S' > Slow, 'C' > Community, 'O' > Other
        """
        # We are checking both 'SlowWallet' and 'Community' occurence in the query output
        with os.popen(f"ol -a {address} query -r | sed -n '/SlowWallet/,/StructTag/p'") as f:
            for elem in f.readlines():
                if 'SlowWallet' in elem:
                    return 'S'
        return 'N'

    def update_wallet_type(obj: Dict) -> None:
        """
        Update wallet type
        """
        ab = session\
            .query(AccountBalance)\
            .filter(AccountBalance.address == obj['address'])\
            .first()
        ab.wallet_type = obj['wallet_type']
        session.commit()
    
    def update_unlocked(obj: Dict) -> None:
        """
        Update unlocked amount
        """
        ab = session\
            .query(AccountBalance)\
            .filter(AccountBalance.address == obj['address'])\
            .first()
        ab.unlocked = obj['unlocked']
        session.commit()

    def lookup_unlocked(address: AnyStr) -> int:
        """
        Checks if a given address is a slow wallet.
        :param address: the address to check
        :return: 
        """        
        amt = 0

        # We are checking both 'SlowWallet' and 'Community' occurence in the query output
        with os.popen(f"ol -a {address} query -u") as f:
            for line in f.readlines():
                if re.search("(UNLOCKED)", line):
                    # print(f"line={line}")
                    amt = int(int(line.split(' ')[2]) / 1000000)
        return amt

    def lookup_wallets_unlocked(self) -> None:
        wallets = session\
            .query(AccountBalance)\
            .filter(
                AccountBalance.balance > 0, AccountBalance.wallet_type == 'S')\
            .all()
        for v in wallets:
            v.unlocked = self.lookup_unlocked(v.address)
        session.commit()
    
    def lookup_wallet_types(self) -> None:
        validators = session\
            .query(AccountBalance)\
            .filter(
                AccountBalance.balance > 0,
                or_(AccountBalance.account_type == 'basic', 
                    AccountBalance.account_type == 'miner'))\
            .all()
        for v in validators:
            v.wallet_type = self.lookup_wallet_type(v.address)
            print(f"{v.address} > {v.wallet_type}")
        session.commit()

    def upload_balances(balance_list: List) -> None:
        try:
            # Iterate objects and store them in the db
            for pe_obj in balance_list:
                ab = session\
                    .query(AccountBalance)\
                    .filter(AccountBalance.address == pe_obj['address'])\
                    .scalar()

                o = AccountBalance(
                    address=pe_obj['address'],
                    balance=int(pe_obj['balance']),
                    account_type=pe_obj['account_type']
                )

                if ab:
                    o.id = ab.id
                    o.unlocked=ab.unlocked,
                    o.wallet_type=ab.wallet_type
                    session.merge(o)
                else:
                    session.add(o)

            session.commit()
        except Exception as e:
            print(f"[{datetime.now()}]:ERROR:{e}")


class AccountTransaction(Base):
    __tablename__ = "accounttransaction"

    id = Column(Integer, primary_key=True)
    hash = Column(LargeBinary(length=64), unique=True)
    address = Column(String(100), nullable=False)
    txtimestamp = Column(DateTime, nullable=False)
    sequence_number = Column(BigInteger, nullable=False)
    response = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def upload_result(address: AnyStr, txlist: List):
        error_row = {}
        try:
            # Iterate objects and store them in the db
            for pe_obj in txlist:
                error_row = pe_obj
                ab = session\
                    .query(AccountTransaction)\
                    .filter(AccountTransaction.hash == pe_obj['hash'].encode('utf-8'))\
                    .scalar()
                
                # jump to next item in loop when hash already exists in db
                if ab:
                    continue

                o = AccountTransaction(
                    hash=pe_obj['hash'].encode('utf-8'),
                    address=address,
                    sequence_number=int(pe_obj['transaction']['sequence_number']),
                    txtimestamp=datetime.fromtimestamp(pe_obj['timestamp_usecs'] / 1000000),
                    response=pe_obj
                )

                session.add(o)

            session.commit()
        except Exception as e:
            print(f"[{datetime.now()}]:ROW:{error_row}:ERROR:{e}")
    
    def max_seq(address):
        return session\
            .query(func.max(AccountTransaction.sequence_number))\
            .where(AccountTransaction.address==address)\
            .scalar()
        


# ALTER TABLE accountbalance ADD COLUMN wallet_type CHAR(1);

Base.metadata.create_all(engine)
