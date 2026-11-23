# Berka Bank: Spotting Risky Loans with SQL

Using SQL on **1,056,320 real bank transactions**, I built three early-warning signals for loan default and shipped them as a live, interactive dashboard. The strongest signal: **borrowers in the lowest 20% by average balance defaulted at 37.50%, about 13 times the 2.85% rate of the highest 20%.**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)

**[View the live dashboard](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)**

| At a glance | |
|---|---|
| Data | 8 linked tables from a Czech bank, 1993 to 1998; 682 loans, 76 of them bad (11.1%) |
| Built | A PostgreSQL database, 3 analytical queries, and a Streamlit + Plotly dashboard |
| Key techniques | Chained CTEs, `NTILE`, `LAG` and `ROW_NUMBER` window functions |
| Performance fix | One query cut from more than an hour to under 5 seconds |

---

## Situation

A Czech bank issued 682 loans, and **76 of them (11.1%) went bad**. The question was whether those borrowers could have been spotted earlier from their everyday account behaviour.

The raw data was not ready to query:

- **Eight semicolon-separated files** that had to be modelled and loaded into a relational database in the right order.
- **A file that wouldn't load:** `district.csv` used `?` for missing values, which PostgreSQL rejects in numeric columns.
- **Czech labels and coded dates:** transaction types such as `PRIJEM` (money in) and `VYBER` (cash withdrawal), and dates stored as `YYMMDD` codes. A wrong label returns a wrong answer with no error.
- **Four loan outcomes, not two:** A (repaid, 203), C (running fine, 403), B (ended unpaid, 31) and D (running, client in trouble, 45).

## Task

Find out whether account behaviour can flag a risky borrower, using SQL alone, and present the results so a non-technical credit team can explore them. I framed it as one question for each stage at which a lender can act:

| Stage | Question |
|---|---|
| Before lending | Do customers who keep more money in their account default less? |
| After lending | Does a sudden drop in account activity signal trouble? |
| Before the final default | Can we spot borrowers pulling their money out ahead of defaulting? |

## Action

**1. Built the database**
- Designed eight PostgreSQL tables with primary and foreign keys, and loaded them in dependency order (district first, card last) through DBeaver.
- Fixed `district.csv` in Python before loading: read `?` as missing (one value each in A12 and A15) and filled them with the column average. This is regional data that the transaction queries don't depend on, so filling beat deleting a district.
- Verified every table's row count after loading (for example, 1,056,320 transactions and 682 loans).

**2. Understood the data before querying it**
- Read the dataset's original project description first.
- Merged the four loan statuses into GOOD (A, C) and BAD (B, D), the binary framing used in credit scoring.
- Translated and counted the Czech transaction labels so every filter used the right one.

**3. Wrote three queries, one technique each**

| Query | Approach | SQL technique |
|---|---|---|
| 1. Balance vs default | Average balance per account, split into five equal groups; compare the bottom and top 20% default rates | Chained CTEs, `NTILE(5)` |
| 2. Activity drop | Transactions per account per month, set beside the previous month; flag drops over 40% | `LAG()` |
| 3. Cash-out | Each BAD-loan account's latest transaction vs its average monthly income; flag outflows above a cut-off | `ROW_NUMBER()` |

**4. Solved three problems along the way**
- **A query that didn't scale.** My first Query 3 looked up each account's latest transaction by re-scanning the table for every row, over a million lookups. It ran for more than an hour. Rewriting it to rank all rows newest first in a single pass with `ROW_NUMBER()` brought it to **under 5 seconds**.
- **A false alarm.** December 1998 kept topping Query 2's drop list. I traced it to the dataset ending partway through that month, so accounts only looked quiet. In production I would exclude the latest, incomplete month.
- **A cut-off with no single right answer.** I ran Query 3 at both 80% and 50% of income and reported both, because where the line sits is a business decision.

**5. Shipped a dashboard**
- Exported each query's results and built an interactive **Streamlit + Plotly** dashboard, so anyone can explore the findings in a browser without SQL.

## Result

| Signal | Finding | How a bank would use it |
|---|---|---|
| Average balance | **37.50%** default rate in the lowest 20% vs **2.85%** in the highest 20%: about **13x** | An input to the credit score |
| Activity drop | Drops of up to **90%** in a month (for example, 18 transactions falling to 3); December 1998 identified as a data artefact | Post-loan monitoring, on completed months only |
| Cash-out | At 80% no account was flagged. At 50%, **account 10857** was flagged: the largest bad loan (385,560), with a last transfer out worth **73.68%** of its monthly income | A fraud check on top of the credit score, with the cut-off set by the credit team |

The Query 3 result is a precision versus recall trade-off. A strict cut-off flags fewer honest customers but misses real risk; a loose one catches more risk but creates more false alarms.

**Limitations and next steps**
- **Query 1 uses balances from the whole account history,** including after each loan was issued. A borrower already in default will show a low balance because of it, which could inflate the 13x gap. Next step: use only transactions dated before each loan.
- **Small groups:** the lowest-balance group has only 40 loans (15 bad), so 37.50% is directional. Comparing all five groups would show whether risk rises steadily with balance.
- **Queries 2 and 3 are not yet validated against outcomes.** Testing them on GOOD loans too would measure how many honest customers each flag would catch.

---

## Tools

| Tool | Use |
|---|---|
| PostgreSQL, DBeaver | Database, table design, data loading, queries |
| Python (pandas) in Google Colab | Fixing the missing values in the district file |
| Python, Streamlit, Plotly | Interactive dashboard |
| Git, GitHub | Version control |

## Repository

```
├── berka_dashboard.py                      # Streamlit dashboard
├── requirements.txt                        # Python dependencies
├── Querying_the_Berka_Bank_Data.sql        # The three queries, with notes
├── Handling_district_missing_values.ipynb  # Fix for the district file
├── README.md
└── data/
    ├── query1_balance_vs_default.csv
    ├── query2_velocity_drop.csv
    ├── query3_cashout_risk_50%.csv         # Query 3 at the 50% cut-off
    └── query4_cashout_risk_80%.csv         # Query 3 at the 80% cut-off
```

---

## Technical Detail

<details>
<summary><b>Query 1 SQL: average balance vs default</b></summary>

```sql
WITH account_avg_balance AS (
    SELECT account_id, ROUND(AVG(balance), 2) AS avg_balance
    FROM trans
    GROUP BY account_id
),
account_percentiles AS (
    SELECT account_id, avg_balance,
           NTILE(5) OVER (ORDER BY avg_balance) AS balance_group
    FROM account_avg_balance
),
top_and_bottom AS (
    SELECT account_id, avg_balance,
           CASE WHEN balance_group = 1 THEN 'BOTTOM 20%'
                WHEN balance_group = 5 THEN 'TOP 20%' END AS balance_tier
    FROM account_percentiles
    WHERE balance_group IN (1, 5)
)
SELECT top_and_bottom.balance_tier,
       COUNT(loan.loan_id) AS total_loans,
       SUM(CASE WHEN loan.status IN ('B','D') THEN 1 ELSE 0 END) AS bad_loans,
       ROUND(SUM(CASE WHEN loan.status IN ('B','D') THEN 1 ELSE 0 END) * 100.0
             / COUNT(loan.loan_id), 2) AS default_rate_percent
FROM top_and_bottom
JOIN loan ON top_and_bottom.account_id = loan.account_id
GROUP BY top_and_bottom.balance_tier
ORDER BY top_and_bottom.balance_tier;
```

All three queries are in `Querying_the_Berka_Bank_Data.sql`.
</details>

<details>
<summary><b>Problems I hit while building the database, and the fixes</b></summary>

| Problem | Cause | Fix |
|---|---|---|
| District file would not load | Missing values written as `?` | Read `?` as missing in pandas and filled with the column average before loading |
| District table didn't match the file | The file's first column is `A1`; the table expected another name | Recreated the table with columns `A1` to `A16` to match the file |
| Error during loading | Some rows broke the table's rules | Turned off batch insert in DBeaver (batch size 1), then confirmed row counts |
| Query 3 ran for over an hour | A correlated lookup repeated for each of 1,056,320 rows | Single-pass ranking with `ROW_NUMBER()` |
| December 1998 looked high risk | The dataset ends partway through the month | Treated as a data artefact; exclude the latest month in production |
</details>

<details>
<summary><b>How to run or rebuild the project</b></summary>

**Option 1: View the results.** Open the [live dashboard](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/). Nothing to install.

**Option 2: Run the dashboard locally** (Python 3.8+; no database needed, since it reads the CSVs in `data/`):

```bash
git clone https://github.com/KathituCodes/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
streamlit run berka_dashboard.py
```

**Option 3: Rebuild the database** (Python 3.8+, PostgreSQL, DBeaver or any PostgreSQL client):

1. **Download** the eight CSVs from [Kaggle](https://www.kaggle.com/datasets/marceloventura/the-berka-dataset). They are semicolon-separated, dates are `YYMMDD`, and labels are in Czech:

   | Czech | English |
   |---|---|
   | PRIJEM | Credit (money in) |
   | VYDAJ | Debit (money out) |
   | VYBER | Cash withdrawal |
   | VKLAD | Cash deposit |
   | PREVOD NA UCET | Transfer to another account |
   | PREVOD Z UCTU | Transfer from another account |
   | VYBER KARTOU | Card withdrawal |

2. **Clean the district file:**

   ```python
   import pandas as pd
   df = pd.read_csv('district.csv', sep=';', na_values=['?'])
   print(df.isnull().sum())                     # A12 and A15 each have 1 missing value
   df['A12'] = df['A12'].fillna(df['A12'].mean())
   df['A15'] = df['A15'].fillna(df['A15'].mean())
   df.to_csv('district_clean.csv', sep=';', index=False)
   ```

   Import `district_clean.csv`, not the original.

3. **Create the tables:**

   ```sql
   CREATE TABLE account (
       account_id   INTEGER PRIMARY KEY,
       district_id  INTEGER,
       frequency    VARCHAR(50),
       date         VARCHAR(10)
   );

   CREATE TABLE client (
       client_id    INTEGER PRIMARY KEY,
       birth_number VARCHAR(10),
       district_id  INTEGER
   );

   CREATE TABLE district (
       A1 INTEGER PRIMARY KEY, A2 VARCHAR(100), A3 VARCHAR(100),
       A4 INTEGER, A5 INTEGER, A6 INTEGER, A7 INTEGER, A8 INTEGER, A9 INTEGER,
       A10 DECIMAL(5,1), A11 INTEGER, A12 DECIMAL(5,2), A13 DECIMAL(5,2),
       A14 INTEGER, A15 INTEGER, A16 INTEGER
   );

   CREATE TABLE disp (
       disp_id    INTEGER PRIMARY KEY,
       client_id  INTEGER REFERENCES client(client_id),
       account_id INTEGER REFERENCES account(account_id),
       type       VARCHAR(20)
   );

   CREATE TABLE loan (
       loan_id    INTEGER PRIMARY KEY,
       account_id INTEGER REFERENCES account(account_id),
       date       VARCHAR(10),
       amount     DECIMAL(12,2),
       duration   INTEGER,
       payments   DECIMAL(12,2),
       status     VARCHAR(2)
   );

   CREATE TABLE "order" (
       order_id   INTEGER PRIMARY KEY,
       account_id INTEGER REFERENCES account(account_id),
       bank_to    VARCHAR(10),
       account_to VARCHAR(20),
       amount     DECIMAL(12,2),
       k_symbol   VARCHAR(20)
   );

   CREATE TABLE trans (
       trans_id   INTEGER PRIMARY KEY,
       account_id INTEGER REFERENCES account(account_id),
       date       VARCHAR(10),
       type       VARCHAR(20),
       operation  VARCHAR(50),
       amount     DECIMAL(12,2),
       balance    DECIMAL(12,2),
       k_symbol   VARCHAR(20),
       bank       VARCHAR(10),
       account    VARCHAR(20)
   );

   CREATE TABLE card (
       card_id  INTEGER PRIMARY KEY,
       disp_id  INTEGER REFERENCES disp(disp_id),
       type     VARCHAR(20),
       issued   VARCHAR(30)
   );
   ```

   District columns: A1 = district ID, A2 = name, A3 = region, A4 = population, A11 = average salary, A12 and A13 = unemployment rate 1995 and 1996, A15 and A16 = crimes 1995 and 1996.

4. **Load the CSVs in this order**, because of the foreign keys: district, account, client, disp, loan, order, trans, card. In DBeaver: right-click the table > **Import Data** > CSV > set the delimiter to `;` > tick **Header row** > Finish. If a batch insert error appears, set the batch size to 1.

5. **Check the row counts:**

   ```sql
   SELECT COUNT(*) FROM account;   -- 4,500
   SELECT COUNT(*) FROM client;    -- 5,369
   SELECT COUNT(*) FROM district;  -- 77
   SELECT COUNT(*) FROM disp;      -- 5,369
   SELECT COUNT(*) FROM loan;      -- 682
   SELECT COUNT(*) FROM "order";   -- 6,471
   SELECT COUNT(*) FROM trans;     -- 1,056,320
   SELECT COUNT(*) FROM card;      -- 892
   ```

   Then run the queries in `Querying_the_Berka_Bank_Data.sql`.
</details>

---

## Connect

- **GitHub:** [github.com/KathituCodes](https://github.com/KathituCodes)
- **Email:** peterkathitu@gmail.com
- **Dashboard:** [Live on Streamlit](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)
