----------------------------------------------------------------------------------------
-- Phase 1: Creating the tables and importing the data. 
----------------------------------------------------------------------------------------

-- Creating the account table
-- Every bank account that exists. Like a list of all bank account numbers.
CREATE TABLE account (
account_id INTEGER PRIMARY KEY,
district_id INTEGER,
frequency VARCHAR(50),
date VARCHAR(10)
);

-- Creating the Client table
-- Every person who is a customer. Name, birthday, which area they live in.
CREATE TABLE client (
client_id INTEGER PRIMARY KEY,
birth_number VARCHAR(10),
district_id INTEGER
);

-- Creating the district table.  
-- Information about the area where the client lives. 
-- Population size, average salary, and crime rate in that region.
CREATE TABLE district (
A1 INTEGER PRIMARY KEY,
A2 VARCHAR(100),
A3 VARCHAR(100),
A4 INTEGER,
A5 INTEGER,
A6 INTEGER,
A7 INTEGER,
A8 INTEGER,
A9 INTEGER,
A10 DECIMAL(5,1),
A11 INTEGER,
A12 DECIMAL(5,2),
A13 DECIMAL(5,2),
A14 INTEGER,
A15 INTEGER,
A16 INTEGER
);

-- Creating the disp table  
-- The link between a person and their account. 
-- One person can own multiple accounts. One account can have multiple people attached to it.
CREATE TABLE disp (
disp_id INTEGER PRIMARY KEY,
client_id INTEGER REFERENCES client(client_id),
account_id INTEGER REFERENCES account(account_id),
type VARCHAR(20)
);

-- Creating the loan table
-- Every loan the bank ever gave out. How much, for how long, and most importantly: did the person pay it back or not? 
-- This is our target, the thing we want to predict.
CREATE TABLE loan (
loan_id INTEGER PRIMARY KEY,
account_id INTEGER REFERENCES account(account_id),
date VARCHAR(10),
amount DECIMAL(12,2),
duration INTEGER,
payments DECIMAL(12,2),
status VARCHAR(2)
);

-- Creating the order table
-- Standing orders. Eample: "every month automatically send this amount to pay my rent."
CREATE TABLE "order" (
order_id INTEGER PRIMARY KEY,
account_id INTEGER REFERENCES account(account_id),
bank_to VARCHAR(10),
account_to VARCHAR(20),
amount DECIMAL(12,2),
k_symbol VARCHAR(20)
);

-- Creating a trans table
-- Every single transaction ever made. Over one million rows. 
-- This is the heartbeat of the whole dataset. Every deposit, withdrawal, and payment ever made.
CREATE TABLE trans (
trans_id INTEGER PRIMARY KEY,
account_id INTEGER REFERENCES account(account_id),
date VARCHAR(10),
type VARCHAR(20),
operation VARCHAR(50),
amount DECIMAL(12,2),
balance DECIMAL(12,2),
k_symbol VARCHAR(20),
bank VARCHAR(10),
account VARCHAR(20)
);

-- Creating the card table
-- Credit cards issued to customers.
CREATE TABLE card (
card_id INTEGER PRIMARY KEY,
disp_id INTEGER REFERENCES disp(disp_id),
type VARCHAR(20),
issued VARCHAR(30)
);

----------------------------------------------------------------------------------------
-- Phase 2 Verifying the data was sucessfully imported correctly. 
----------------------------------------------------------------------------------------

-- Lets check for the count (Number of rows for each table)

-- Expected count (4500 rows)
SELECT COUNT(*) FROM account;

-- Expected count (5369 rows)
SELECT COUNT(*) FROM client;

-- Expected count (77 rows)
SELECT COUNT(*) FROM district;

-- Expected count (5369 rows)
SELECT COUNT(*) FROM disp;

-- Expected count (682 rows)
SELECT COUNT(*) FROM loan;

-- Expected count (6471 rows)
SELECT COUNT(*) FROM "order";

-- Expected count (1,056,320 rows)
SELECT COUNT(*) FROM trans;

-- Expected count (892 rows)
SELECT COUNT(*) FROM card;

----------------------------------------------------------------------------------------
-- Phase 3 Understanding the data I will be querying. 
----------------------------------------------------------------------------------------

-- We need to understand the loan data before doing any analysis.
-- The 'status' column tells us whether a loan was paid back or not.
-- This query counts how many loans fall into each status category, we group them by the status.
SELECT status, COUNT(*) AS total_loans  
FROM loan
GROUP BY status       -- Group all loans together by their status letter
ORDER BY total_loans DESC;  -- Show the most common status first

-- From the resuts of the data above these are the interpretations
-- reference: https://webpages.charlotte.edu/mirsad/itcs6265/group1/loan_domain.html
-- A = Loan finished, client paid everything back on time. GOOD CLIENT.
-- B = Loan finished, but client did NOT pay it all back. BAD CLIENT.
-- C = Loan is still running, no problems so far. CURRENTLY GOOD.
-- D = Loan is still running, but client is already in debt trouble. CURRENTLY BAD.

-- A and C = people the bank is happy with
-- B and D = people the bank lost money on or is worried about

-- 606 are good or currently fine (A + C)
-- 76 are bad or in trouble (B + D)

-- This is the credit risk problem lending companies solves every day 
-- So the question at hand is how do you identify the 76 bad ones before you give them money?
-- For my project I will simplify this into two groups. Good and Bad. 

-- Create a simple binary label for each loan.
-- Good = the bank is happy (A or C)
-- Bad = the bank lost money or is worried (B or D)
-- This is the foundation of every credit risk model.

SELECT loan_id,account_id,amount,duration,status,
CASE 
WHEN status IN ('A', 'C') THEN 'GOOD'	-- Client paid or is keeping up with payments
WHEN status IN ('B', 'D') THEN 'BAD'   -- Client defaulted (LOAN NOT PAID) or clients (IN DEBT)
END AS risk_label                           -- New simplified risk column
FROM loan
ORDER BY risk_label;

-- The trans table has over 1 million rows.
-- Before we analyse it we need to understand what is inside it.
-- This query shows us every unique transaction type and operation
-- so we know what we are working with.

SELECT type, operation,      -- Whether money came in or went out and what kind of transaction it was                  
COUNT(*) AS total            -- How many times this combination appears
FROM trans
GROUP BY type, operation
ORDER BY total DESC;

-- Reference about what each type stands for: https://webpages.charlotte.edu/mirsad/itcs6265/group1/transaction_domain.html
-- Doc with transaction labels and breakdown: https://docs.google.com/document/d/1agnnl9gg35QQy9K4aESNbf_Xx80LagO6BIyG4eswVbA/edit?tab=t.0

----------------------------------------------------------------------------------------
-- Phase 4 Querying the data to make some business analysis. 
----------------------------------------------------------------------------------------

-- Question 1: Do high balance accounts default less?
-- This is the question most fintech credit team asks. If a client has a high average balance, are they safer to lend to?

-- QUERY 1: Average monthly balance per account vs loan default rate
-- Step 1: We calculate the average balance for every account using all their transactions.
-- Step 2: We split accounts into TOP 20% and BOTTOM 20% by average balance.
-- Step 3: We check what percentage of each group defaulted on their loan.

-- This will inform us if having more money in your account means you are safer to lend to?
-- Run the entire query together

WITH account_avg_balance as (
SELECT account_id,
ROUND(AVG(balance), 2) AS avg_balance  -- Average balance across all transactions
FROM trans
GROUP BY account_id
),

account_percentiles AS (
    -- Now I ranked every account by their average balance
    -- used NTILE(5) to split all accounts into 5 equal groups (quintiles)
    -- Group 1 = bottom 20% (poorest balances)
    -- Group 5 = top 20% (richest balances)
SELECT account_id,avg_balance,
NTILE(5) OVER (ORDER BY avg_balance) AS balance_group
FROM account_avg_balance
),

top_and_bottom AS (
-- We only want the top 20% and bottom 20% for comparison
SELECT account_id,avg_balance,
CASE 
WHEN balance_group = 1 THEN 'BOTTOM 20%'  -- Lowest balances
WHEN balance_group = 5 THEN 'TOP 20%'     -- Highest balances
END AS balance_tier
FROM account_percentiles
WHERE balance_group IN (1, 5)  -- Filter to only top and bottom groups
)

-- Final step: join to the loan table and check default rates
SELECT top_and_bottom.balance_tier,
COUNT(loan.loan_id) AS total_loans,
SUM(CASE WHEN loan.status IN ('B','D') THEN 1 ELSE 0 END)  AS bad_loans,
ROUND(SUM(CASE WHEN loan.status IN ('B','D') THEN 1 ELSE 0 END) * 100.0
/ COUNT(loan.loan_id), 2) AS default_rate_percent
FROM top_and_bottom
JOIN loan ON top_and_bottom.account_id = loan.account_id
GROUP BY top_and_bottom.balance_tier
ORDER BY top_and_bottom.balance_tier;

-- This query shows us :
-- A 13x gap in default risk between the two groups
-- BOTTOM 20% = accounts with the lowest balances
-- A total of 40 loans were given out, 15 went bad, 37.50% default rate

-- TOP 20% = accounts with the highest balances
-- A total of 246 loans were given out, 7 went bad, 2.85% default rate

-- The data shows that if you lend money to someone with a consistently low bank balance, 37 out of every 100 loans go bad.
-- The data shows that if you lend money to someone with a consistently high bank balance, only 3 out of every 100 loans go bad.
-- That is a significant difference in risk. Average balance is clearly a strong signal of creditworthiness.


-- Question 2: Are there any month-over-monthly transaction velocity Drop occurances?
-- Velocity drop is when an account experiences a sudden drop in transaction activity and it is one of the earliest warning signs of default risk.
-- The aim is to flag any account whose transaction count dropped more than 40% compared to the previous month or in a single month.
-- A sudden drop in transaction activity often means financial trouble.

WITH monthly_transaction_counts AS (
-- Step 1: Count how many transactions each account made per month
-- We extract the year and month from the date column
-- The date is stored as YYMMDD text so we convert it first
select trans.account_id,
-- Convert the stored date format YYMMDD into a real year and month
CAST(CONCAT('19', SUBSTRING(trans.date::TEXT, 1, 2)) AS INTEGER) AS txn_year,
CAST(SUBSTRING(trans.date::TEXT, 3, 2) AS INTEGER) AS txn_month,
COUNT(trans.trans_id) AS txn_count
FROM trans
GROUP by trans.account_id,
CAST(CONCAT('19', SUBSTRING(trans.date::TEXT, 1, 2)) AS INTEGER),
CAST(SUBSTRING(trans.date::TEXT, 3, 2) AS INTEGER)
),

monthly_with_previous AS (
-- Step 2: For each account and month, look back and grab last month's count
-- LAG() is the window function that reaches back one row
-- PARTITION BY account_id means we restart the look-back for each account
-- ORDER BY year and month means we go in chronological order
SELECT
monthly_transaction_counts.account_id,
monthly_transaction_counts.txn_year,
monthly_transaction_counts.txn_month,
monthly_transaction_counts.txn_count AS current_month_txns,
LAG(monthly_transaction_counts.txn_count) 
OVER (PARTITION BY monthly_transaction_counts.account_id      -- Restart for each account
ORDER BY 
monthly_transaction_counts.txn_year,                -- Go in year order
monthly_transaction_counts.txn_month                -- Then month order
) AS previous_month_txns
FROM monthly_transaction_counts
),

velocity_drop AS (
-- Step 3: Calculate the percentage drop from last month to this month
-- We only look at rows where we have a previous month to compare against
-- previous_month_txns IS NOT NULL filters out the very first month per account
SELECT
monthly_with_previous.account_id,
monthly_with_previous.txn_year,
monthly_with_previous.txn_month,
monthly_with_previous.current_month_txns,
monthly_with_previous.previous_month_txns,
-- Calculate percentage change from previous month to current month
ROUND((monthly_with_previous.current_month_txns - monthly_with_previous.previous_month_txns) * 100.0 
/ monthly_with_previous.previous_month_txns, 2) AS pct_change
FROM monthly_with_previous
WHERE monthly_with_previous.previous_month_txns IS NOT NULL  -- Need a previous month to compare
)

-- Final step: flag accounts with a drop greater than 40%
-- A drop means the percentage change is negative and below -40
SELECT
velocity_drop.account_id,
velocity_drop.txn_year,
velocity_drop.txn_month,
velocity_drop.current_month_txns,
velocity_drop.previous_month_txns,
velocity_drop.pct_change,
-- Flag accounts whose transaction count dropped more than 40%
CASE
WHEN velocity_drop.pct_change < -40 THEN 'HIGH RISK: Activity Drop > 40%'
WHEN velocity_drop.pct_change < -20 THEN 'MEDIUM RISK: Activity Drop > 20%'
ELSE 'NORMAL'
END AS risk_flag
FROM velocity_drop
WHERE velocity_drop.pct_change < -40  -- Only show the high risk accounts
ORDER BY velocity_drop.pct_change ASC -- Worst drops first
LIMIT 20;


-- Question 3: When you borrowed money from a bank and know you cannot pay it back. What do you do?
-- Sometimes clients withdraw as much cash as possible from their account before they stop paying. 
-- This is called "Cash out before default" and it is a real fraud pattern that fintech credit teams watch for actively.

-- QUERY 3: Cash out before default risk detection
-- We are looking for accounts that meet 2 conditions simultaneously:
-- Condition 1: They have a loan that is bad or in trouble (status B or D)
-- Condition 2: Their recent transaction was a cash withdrawal that was larger than 80% of their average monthly inflow

-- These two signals together indicate possible intentional cash out before default.
-- We now use ROW_NUMBER() window function to find the latest transaction per account in a single pass over the data instead of 1 million subqueries.

WITH account_income_profile AS (
-- Calculate average monthly inflow for every account
-- Only looking at incoming transactions (PRIJEM = credit)
SELECT
trans.account_id,
ROUND(AVG(trans.amount), 2) AS avg_monthly_inflow
FROM trans
WHERE trans.type = 'PRIJEM'
GROUP BY trans.account_id
),

ranked_transactions AS (
-- Rank every transaction per account by date descending
-- ROW_NUMBER() assigns rank 1 to the most recent transaction
-- PARTITION BY account_id means ranking restarts for each account
-- ORDER BY date DESC means the latest date gets rank 1
SELECT
trans.account_id,
trans.date AS txn_date,
trans.type AS txn_type,
trans.operation AS txn_operation,
trans.amount AS txn_amount,
ROW_NUMBER() OVER (PARTITION BY trans.account_id   -- Restart ranking for each account
ORDER BY trans.date DESC) AS row_rank  -- Latest date first
FROM trans
),

latest_transaction AS (
-- Keep only rank 1 which is the most recent transaction per account
SELECT
ranked_transactions.account_id,
ranked_transactions.txn_date AS last_txn_date,
ranked_transactions.txn_type AS last_txn_type,
ranked_transactions.txn_operation AS last_txn_operation,
ranked_transactions.txn_amount AS last_txn_amount
FROM ranked_transactions
WHERE ranked_transactions.row_rank = 1
),

bad_loan_accounts AS (
-- Find all accounts with a bad or troubled loan
-- Status B = finished but not fully repaid
-- Status D = still running but already in trouble
SELECT
loan.account_id,
loan.loan_id,
loan.amount AS loan_amount,
loan.status AS loan_status
FROM loan
WHERE loan.status IN ('B', 'D')
)

-- Bring everything together and flag high risk accounts
SELECT
    bad_loan_accounts.account_id,
    bad_loan_accounts.loan_id,
    bad_loan_accounts.loan_amount,
    bad_loan_accounts.loan_status,
    latest_transaction.last_txn_date,
    latest_transaction.last_txn_type,
    latest_transaction.last_txn_operation,
    latest_transaction.last_txn_amount,
    account_income_profile.avg_monthly_inflow,
    -- What percentage of their average inflow was this last withdrawal
ROUND(latest_transaction.last_txn_amount * 100.0
/ account_income_profile.avg_monthly_inflow, 2) AS withdrawal_as_pct_of_income,
 -- Flag accounts where last transaction was a large cash withdrawal
CASE
WHEN latest_transaction.last_txn_type = 'VYDAJ'
AND latest_transaction.last_txn_amount > (account_income_profile.avg_monthly_inflow * 0.50) -- Threshold lowered from 80% to 50% to monitor how risk levels change
THEN 'HIGH RISK: Large withdrawal on bad loan account'
ELSE 'MONITOR'
END AS risk_flag
FROM bad_loan_accounts
JOIN latest_transaction
ON bad_loan_accounts.account_id = latest_transaction.account_id
JOIN account_income_profile
ON bad_loan_accounts.account_id = account_income_profile.account_id
WHERE latest_transaction.last_txn_type = 'VYDAJ'
ORDER BY withdrawal_as_pct_of_income DESC;


