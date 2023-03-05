with base as (select account_type, sum(balance / 1000000) as balance, sum(unlocked) as unlocked from accountbalance where balance > 0 group by account_type), bla as ( select account_type, balance, unlocked, case account_type when 'basic' then balance when 'validator' then unlocked when 'miner' then balance else 0 end as liquid from base) select account_type, balance, unlocked, liquid from bla UNION select 'TOTALS', sum(balance), sum(unlocked), sum(liquid) from bla order by 1 desc;

with base as (
    select 
        account_type,
        wallet_type, 
        sum(balance/1000000) as balance, 
        sum(case 
            when account_type = 'community' then 0
            when wallet_type = 'N' then balance/1000000
            when unlocked <= (balance/1000000) then unlocked 
            else balance/1000000
            end) as unlocked
    from accountbalance 
    where (balance/1000000) > 0 
    group by account_type, wallet_type
) 
select 
    account_type,
    wallet_type, 
    balance, 
    unlocked 
from base 
UNION 
select 'TOTALS', '=>', sum(balance), sum(unlocked) from base order by 3


select account_type, sum(balance) as balance
from accountbalance
group by account_type
order by 2

select id, balance/1000000 as balance, unlocked
from accountbalance
where wallet_type = 'V'
and unlocked > balance/1000000

select 
    row_number() OVER(order by balance desc) as row,
    address, 
    account_type, 
    balance / 1000000 as balance
from accountbalance 
where account_type in ('miner','validator','basic') 
order by balance desc;

select 
    row_number() OVER(order by balance desc) as row,
    address, 
    account_type,
    case wallet_type 
        when 'N' then 'liquid' 
        when 'V' then 'validator' 
        when 'C' then 'community' 
        when 'S' then 'slow'
        else 'unknown' 
    end as wallet_type,
    balance / 1000000 as balance
from accountbalance 
where account_type in ('miner','validator','basic') 
order by balance desc;

select 
    -- txtimestamp, response
    -- max() as max_seq_nr
    count(*) as cnt,
    max(response->'transaction'->>'sequence_number') max_seq
from accounttransaction
where (response::jsonb->'transaction'->>'sequence_number') > 999
-- order by txtimestamp desc;

--truncate table accounttransaction;

select 
    distinct
    txtimestamp,
    -- max() as max_seq_nr
    -- count(*) as cnt,
    -- max(response->'transaction'->>'sequence_number') max_seq
    -- response->'transaction'->'script'->>'function_name'
    response
from accounttransaction
where response->'transaction'->'script'->>'function_name' not in ('minerstate_commit')
-- where (response::jsonb->'transaction'->>'sequence_number') > 999
order by txtimestamp desc;
-- limit 1000


-- response->'transaction'->'script'->>'function_name'
-- 'vouch_for'
-- 'voucher_unjail'
-- 'balance_transfer'
-- 'minerstate_commit'
-- 'create_user_by_coin_tx'
-- 'autopay_create_instruction'
-- 'create_acc_val'

SELECT pg_size_pretty( pg_database_size('viz_dev'));

select distinct cast(response->'transaction'->>'sequence_number' as int) as seq
from accounttransaction
-- where response->'transaction'->>'sequence_number' is null
order by 1



select account_type, count(*) as cnt
from accountbalance
group by account_type
