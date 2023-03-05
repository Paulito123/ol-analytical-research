with base as (select account_type, sum(balance / 1000000) as balance, sum(unlocked) as unlocked from accountbalance where balance > 0 group by account_type), bla as ( select account_type, balance, unlocked, case account_type when 'basic' then balance when 'validator' then unlocked when 'miner' then balance else 0 end as liquid from base) select account_type, balance, unlocked, liquid from bla UNION select 'TOTALS', sum(balance), sum(unlocked), sum(liquid) from bla order by 1 desc;

with base as (
    select 
        wallet_type, 
        sum(balance/1000000) as balance, 
        sum(case 
            when wallet_type = 'N' then balance/1000000 
            when unlocked <= (balance/1000000) then unlocked 
            else balance/1000000
            end) as unlocked
    from accountbalance 
    where (balance/1000000) > 0 
    group by wallet_type
) 
select 
    wallet_type, 
    balance, 
    unlocked 
from base 
UNION 
select 'TOTALS', sum(balance), sum(unlocked) from base order by 3

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


-- select distinct response->'transaction'->'script'->>'function_name' from accounttransaction;
-- 'revoke_vouch'
-- 'rotate_authentication_key'
-- 'community_transfer'
-- 'ol_remove_delegation'
-- 'autopay_create_instruction'
-- 'autopay_disable'
-- 'autopay_enable'
-- 'claim_make_whole'
-- 'vouch_for'
-- 'voucher_unjail'
-- 'balance_transfer'
-- 'minerstate_commit'
-- 'create_user_by_coin_tx'
-- 'create_acc_val'
-- 'demo_e2e'
-- 'set_burn_pref'
-- 'join'
-- 'minerstate_commit_by_operator'
-- 'ol_delegate_vote'
-- 'ol_enable_delegation'
-- 'ol_oracle_tx'
-- 'ol_revoke_vote'
-- 'register_validator_config'
-- 'self_unjail'
-- 'set_wallet_type'

with a as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'minerstate_commit_by_operator' and response->'vm_status'->>'type' = 'executed' limit 1), b as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'ol_delegate_vote' and response->'vm_status'->>'type' = 'executed' limit 1), c as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'ol_enable_delegation' and response->'vm_status'->>'type' = 'executed' limit 1), d as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'ol_oracle_tx' and response->'vm_status'->>'type' = 'executed' limit 1), e as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'ol_revoke_vote' and response->'vm_status'->>'type' = 'executed' limit 1), f as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'register_validator_config' and response->'vm_status'->>'type' = 'executed' limit 1), g as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'self_unjail' and response->'vm_status'->>'type' = 'executed' limit 1), h as (select response from accounttransaction where response->'transaction'->'script'->>'function_name' = 'set_wallet_type' and response->'vm_status'->>'type' = 'executed' limit 1) select response from a union all select response from b union all select response from c union all select response from d union all select response from e union all select response from f union all select response from g union all select response from h;



-- select distinct response->'vm_status'->>'type' from accounttransaction order by 1;
-- 'executed'
-- 'execution_failure'
-- 'miscellaneous_error'
-- 'move_abort'
-- 'out_of_gas'

-- Columns to be created:
-- > vm_status out of response->'vm_status'->>'type'
alter table accounttransaction add column vm_status_type varchar(50) generated always as (response->'vm_status'->>'type') stored;
-- > function_name out of response->'transaction'->'script'->>'function_name'
alter table accounttransaction add column function_name varchar(50) generated always as (response->'transaction'->'script'->>'function_name') stored;



SELECT pg_size_pretty(pg_database_size('adhoc'));

select distinct cast(response->'transaction'->>'sequence_number' as int) as seq
from accounttransaction
-- where response->'transaction'->>'sequence_number' is null
order by 1


with gas_used as (
    select sum(cast(response->>'gas_used' as float)) 
    from accounttransaction 
    where address = '2bfd96d8a674a360b733d16c65728d72'
)
, 



select account_type, count(*) as cnt
from accountbalance
group by account_type

select account_type, count(*) from accounttransaction group by account_type;




with revoke_vouch as (select 'revoke_vouch'                  as func from accounttransaction where function_name = 'revoke_vouch' limit 1)                              
, rotate_authentication_key     as (select 'rotate_authentication_key'     as func from accounttransaction where function_name = 'rotate_authentication_key' limit 1)                              
, community_transfer            as (select 'community_transfer'            as func from accounttransaction where function_name = 'community_transfer' limit 1)                              
, ol_remove_delegation          as (select 'ol_remove_delegation'          as func from accounttransaction where function_name = 'ol_remove_delegation' limit 1)                              
, autopay_create_instruction    as (select 'autopay_create_instruction'    as func from accounttransaction where function_name = 'autopay_create_instruction' limit 1)                              
, autopay_disable               as (select 'autopay_disable'               as func from accounttransaction where function_name = 'autopay_disable' limit 1)                              
, autopay_enable                as (select 'autopay_enable'                as func from accounttransaction where function_name = 'autopay_enable' limit 1)                              
, claim_make_whole              as (select 'claim_make_whole'              as func from accounttransaction where function_name = 'claim_make_whole' limit 1)                              
, vouch_for                     as (select 'vouch_for'                     as func from accounttransaction where function_name = 'vouch_for' limit 1)                              
, voucher_unjail                as (select 'voucher_unjail'                as func from accounttransaction where function_name = 'voucher_unjail' limit 1)                              
, balance_transfer              as (select 'balance_transfer'              as func from accounttransaction where function_name = 'balance_transfer' limit 1)                              
, minerstate_commit             as (select 'minerstate_commit'             as func from accounttransaction where function_name = 'minerstate_commit' limit 1)                              
, create_user_by_coin_tx        as (select 'create_user_by_coin_tx'        as func from accounttransaction where function_name = 'create_user_by_coin_tx' limit 1)                              
, create_acc_val                as (select 'create_acc_val'                as func from accounttransaction where function_name = 'create_acc_val' limit 1)                              
, demo_e2e                      as (select 'demo_e2e'                      as func from accounttransaction where function_name = 'demo_e2e' limit 1)                              
, set_burn_pref                 as (select 'set_burn_pref'                 as func from accounttransaction where function_name = 'set_burn_pref' limit 1)                              
, join_                         as (select 'join'                          as func from accounttransaction where function_name = 'join' limit 1)                              
, minerstate_commit_by_operator as (select 'minerstate_commit_by_operator' as func from accounttransaction where function_name = 'minerstate_commit_by_operator' limit 1)                              
, ol_delegate_vote              as (select 'ol_delegate_vote'              as func from accounttransaction where function_name = 'ol_delegate_vote' limit 1)                              
, ol_enable_delegation          as (select 'ol_enable_delegation'          as func from accounttransaction where function_name = 'ol_enable_delegation' limit 1)                              
, ol_oracle_tx                  as (select 'ol_oracle_tx'                  as func from accounttransaction where function_name = 'ol_oracle_tx' limit 1)                              
, ol_revoke_vote                as (select 'ol_revoke_vote'                as func from accounttransaction where function_name = 'ol_revoke_vote' limit 1)                              
, register_validator_config     as (select 'register_validator_config'     as func from accounttransaction where function_name = 'register_validator_config' limit 1)                              
, self_unjail                   as (select 'self_unjail'                   as func from accounttransaction where function_name = 'self_unjail' limit 1)                              
, set_wallet_type               as (select 'set_wallet_type'               as func from accounttransaction where function_name = 'set_wallet_type' limit 1)                              
select func from revoke_vouch                  union all
select func from rotate_authentication_key     union all
select func from community_transfer            union all
select func from ol_remove_delegation          union all
select func from autopay_create_instruction    union all
select func from autopay_disable               union all
select func from autopay_enable                union all
select func from claim_make_whole              union all
select func from vouch_for                     union all
select func from voucher_unjail                union all
select func from balance_transfer              union all
select func from minerstate_commit             union all
select func from create_user_by_coin_tx        union all
select func from create_acc_val                union all
select func from demo_e2e                      union all
select func from set_burn_pref                 union all
select func from join_                         union all
select func from minerstate_commit_by_operator union all
select func from ol_delegate_vote              union all
select func from ol_enable_delegation          union all
select func from ol_oracle_tx                  union all
select func from ol_revoke_vote                union all
select func from register_validator_config     union all
select func from self_unjail                   union all
select func from set_wallet_type


with revoke_vouch as (select 'revoke_vouch' as func from accounttransaction where function_name = 'revoke_vouch'  and jsonb_array_length(response->'events') > 0 limit 1), rotate_authentication_key as (select 'rotate_authentication_key' as func from accounttransaction where function_name = 'rotate_authentication_key'  and jsonb_array_length(response->'events') > 0 limit 1), community_transfer as (select 'community_transfer' as func from accounttransaction where function_name = 'community_transfer'  and jsonb_array_length(response->'events') > 0 limit 1), ol_remove_delegation as (select 'ol_remove_delegation' as func from accounttransaction where function_name = 'ol_remove_delegation'  and jsonb_array_length(response->'events') > 0 limit 1), autopay_create_instruction as (select 'autopay_create_instruction' as func from accounttransaction where function_name = 'autopay_create_instruction'  and jsonb_array_length(response->'events') > 0 limit 1), autopay_disable as (select 'autopay_disable' as func from accounttransaction where function_name = 'autopay_disable'  and jsonb_array_length(response->'events') > 0 limit 1), autopay_enable as (select 'autopay_enable' as func from accounttransaction where function_name = 'autopay_enable'  and jsonb_array_length(response->'events') > 0 limit 1), claim_make_whole as (select 'claim_make_whole' as func from accounttransaction where function_name = 'claim_make_whole'  and jsonb_array_length(response->'events') > 0 limit 1), vouch_for as (select 'vouch_for' as func from accounttransaction where function_name = 'vouch_for'  and jsonb_array_length(response->'events') > 0 limit 1), voucher_unjail as (select 'voucher_unjail' as func from accounttransaction where function_name = 'voucher_unjail'  and jsonb_array_length(response->'events') > 0 limit 1), balance_transfer as (select 'balance_transfer' as func from accounttransaction where function_name = 'balance_transfer'  and jsonb_array_length(response->'events') > 0 limit 1), minerstate_commit as (select 'minerstate_commit' as func from accounttransaction where function_name = 'minerstate_commit'  and jsonb_array_length(response->'events') > 0 limit 1), create_user_by_coin_tx as (select 'create_user_by_coin_tx' as func from accounttransaction where function_name = 'create_user_by_coin_tx'  and jsonb_array_length(response->'events') > 0 limit 1), create_acc_val as (select 'create_acc_val' as func from accounttransaction where function_name = 'create_acc_val'  and jsonb_array_length(response->'events') > 0 limit 1), demo_e2e as (select 'demo_e2e' as func from accounttransaction where function_name = 'demo_e2e'  and jsonb_array_length(response->'events') > 0 limit 1), set_burn_pref as (select 'set_burn_pref' as func from accounttransaction where function_name = 'set_burn_pref'  and jsonb_array_length(response->'events') > 0 limit 1), join_ as (select 'join' as func from accounttransaction where function_name = 'join'  and jsonb_array_length(response->'events') > 0 limit 1), minerstate_commit_by_operator as (select 'minerstate_commit_by_operator' as func from accounttransaction where function_name = 'minerstate_commit_by_operator'  and jsonb_array_length(response->'events') > 0 limit 1), ol_delegate_vote as (select 'ol_delegate_vote' as func from accounttransaction where function_name = 'ol_delegate_vote'  and jsonb_array_length(response->'events') > 0 limit 1), ol_enable_delegation as (select 'ol_enable_delegation' as func from accounttransaction where function_name = 'ol_enable_delegation'  and jsonb_array_length(response->'events') > 0 limit 1), ol_oracle_tx as (select 'ol_oracle_tx' as func from accounttransaction where function_name = 'ol_oracle_tx'  and jsonb_array_length(response->'events') > 0 limit 1), ol_revoke_vote as (select 'ol_revoke_vote' as func from accounttransaction where function_name = 'ol_revoke_vote'  and jsonb_array_length(response->'events') > 0 limit 1), register_validator_config as (select 'register_validator_config' as func from accounttransaction where function_name = 'register_validator_config'  and jsonb_array_length(response->'events') > 0 limit 1), self_unjail as (select 'self_unjail' as func from accounttransaction where function_name = 'self_unjail'  and jsonb_array_length(response->'events') > 0 limit 1), set_wallet_type as (select 'set_wallet_type' as func from accounttransaction where function_name = 'set_wallet_type'  and jsonb_array_length(response->'events') > 0 limit 1) select func from revoke_vouch union all select func from rotate_authentication_key union all select func from community_transfer union all select func from ol_remove_delegation union all select func from autopay_create_instruction union all select func from autopay_disable union all select func from autopay_enable union all select func from claim_make_whole union all select func from vouch_for union all select func from voucher_unjail union all select func from balance_transfer union all select func from minerstate_commit union all select func from create_user_by_coin_tx union all select func from create_acc_val union all select func from demo_e2e union all select func from set_burn_pref union all select func from join_ union all select func from minerstate_commit_by_operator union all select func from ol_delegate_vote union all select func from ol_enable_delegation union all select func from ol_oracle_tx union all select func from ol_revoke_vote union all select func from register_validator_config union all select func from self_unjail union all select func from set_wallet_type;
-- >>
-- claim_make_whole
-- balance_transfer
-- create_user_by_coin_tx
-- create_acc_val

select function_name, count(*) from accounttransaction where function_name in ('claim_make_whole', 'balance_transfer', 'create_user_by_coin_tx', 'create_acc_val')