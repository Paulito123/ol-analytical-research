from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, BigInteger, Float

# create engine for connecting to ClickHouse
engine = create_engine('clickhouse://olfyi:e588d49c84f1db27e421a379ad1036b8@51.159.101.31:8123/olfyi')

# create metadata object
metadata = MetaData()

# define table schema
burn = Table('burn', metadata,
    Column('version', BigInteger, primary_key=True),
    Column('timestamp_usecs', BigInteger),
    Column('amount', BigInteger),
    Column('currency', String),
    Column('preburn_address', String),
)

# select data from table
select_stmt = burn.select().limit(10)
result = engine.execute(select_stmt)

# print out the result set
for row in result:
    print(row)
