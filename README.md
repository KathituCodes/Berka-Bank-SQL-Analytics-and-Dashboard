# Berka Bank SQL Analytics and Dashboard

---

## Live Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)

**[View the live dashboard here](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)**

---

## Project Overview

This project applies advanced SQL techniques to over one million real bank transactions from the Berka Financial Dataset, a Czech bank dataset covering 1993 to 1998. The goal is to extract credit risk insights that a fintech data team would use in a production lending environment.

Three analytical queries were written in PostgreSQL using CTEs, window functions, and subqueries. The results were exported and visualised in an interactive Streamlit dashboard.

| Query | Business Question | SQL Technique |
|---|---|---|
| 1 | Do high-balance accounts default less on loans? | CTEs + NTILE window function |
| 2 | Can a drop in transaction activity signal default risk? | CTEs + LAG window function |
| 3 | Can we detect cash-out behaviour before default? | CTEs + ROW_NUMBER window function |

---

## Dataset

The Berka dataset contains real financial records from a Czech bank. It is structured across eight relational tables.

| Table | Rows | Description |
|---|---|---|
| account | 4,500 | Every bank account |
| client | 5,369 | Every customer |
| district | 77 | Regional demographic data |
| disp | 5,369 | Links clients to accounts |
| loan | 682 | Every loan issued, including repayment outcome |
| order | 6,471 | Standing payment orders |
| trans | 1,056,320 | Every single transaction |
| card | 892 | Credit cards issued |

**Download:** [Kaggle — The Berka Dataset](https://www.kaggle.com/datasets/marceloventura/the-berka-dataset)

---

## Tools and Stack

- **Database:** PostgreSQL
- **SQL Client:** DBeaver
- **Data Cleaning:** Python (pandas, numpy) in Google Colab
- **Dashboard:** Python, Streamlit, Plotly
- **Version Control:** Git, GitHub

---

## Repository Structure

```
├── berka_dashboard.py               # Streamlit dashboard application
├── requirements.txt                 # Python dependencies for Streamlit Cloud
├── README.md                        # This file
├── Querying_the_Berka_Bank_Data.sql # All three annotated SQL queries
├── Handling_district_missing_values.ipynb  # Data cleaning notebook
└── data/
    ├── query1_balance_vs_default.csv
    ├── query2_velocity_drop.csv
    ├── query3_cashout_risk_50%.csv
    └── query4_cashout_risk_80%.csv
```

---

## Setup and Running Locally

### Prerequisites

- Python 3.8 or higher
- PostgreSQL installed locally
- DBeaver (or any PostgreSQL client)

### Step 1: Clone the repository

```bash
git clone https://github.com/KathituCodes/your-repo-name.git
cd your-repo-name
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the dashboard

```bash
streamlit run berka_dashboard.py
```

---

## Data Preparation

### Step 1: Download and inspect the raw files

Download the eight CSV files from Kaggle. The files use a **semicolon (`;`)** as the delimiter, not a comma. The date column is stored in `YYMMDD` format, not a standard date type. The text is in Czech; key terms are translated below.

| Czech Term | English Meaning |
|---|---|
| PRIJEM | Credit (money coming in) |
| VYDAJ | Debit (money going out) |
| VYBER | Cash withdrawal |
| VKLAD | Cash deposit |
| PREVOD NA UCET | Transfer to another account |
| PREVOD Z UCTU | Transfer from another account |
| VYBER KARTOU | Credit card withdrawal |

### Step 2: Fix missing values in the district file

The `district.csv` file contains question marks (`?`) in two columns where values are missing: **A12** and **A15**. PostgreSQL cannot import question marks into numeric columns and throws the following error:

```
Can't parse numeric value [?] using formatter
Invalid argument: Character ? is neither a decimal digit number,
decimal point, nor "e" notation exponential mark.
```

**Fix using Python (Google Colab or local):**

```python
import pandas as pd

# Read the file, treating ? as NaN
df = pd.read_csv('district.csv', sep=';', na_values=['?'])

# Confirm which columns have missing values
print("Missing values per column:")
print(df.isnull().sum())
# Output: A12 has 1 missing value, A15 has 1 missing value

# Check the affected rows
print(df[df.isnull().any(axis=1)])
```

**Decision rationale:** Since the missing data is regional demographic information (not transactional data), it will not affect the accuracy of transaction-level queries. Filling with the column mean is appropriate here because it is quick, preserves the overall distribution, and avoids reducing the dataset size.

```python
# Fill missing values with the column mean
df['A12'] = df['A12'].fillna(df['A12'].mean())
df['A15'] = df['A15'].fillna(df['A15'].mean())

# Verify no remaining missing values
print("Missing values after cleaning:")
print(df.isnull().sum())
# All columns should now show 0

# Save the cleaned file
df.to_csv('district_clean.csv', sep=';', index=False)
print("Clean file saved successfully")
```

Use `district_clean.csv` for all subsequent imports. The original `district.csv` should not be imported into PostgreSQL.

### Step 3: Create the database tables in DBeaver

Open DBeaver, connect to your PostgreSQL database, open a new SQL script, and run the following:

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
    A1   INTEGER PRIMARY KEY,
    A2   VARCHAR(100),
    A3   VARCHAR(100),
    A4   INTEGER,
    A5   INTEGER,
    A6   INTEGER,
    A7   INTEGER,
    A8   INTEGER,
    A9   INTEGER,
    A10  DECIMAL(5,1),
    A11  INTEGER,
    A12  DECIMAL(5,2),
    A13  DECIMAL(5,2),
    A14  INTEGER,
    A15  INTEGER,
    A16  INTEGER
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

> **Note on the district table:** The column names A1 through A16 match the CSV headers exactly. After importing, A1 serves as the district_id primary key. The remaining columns map to: A2 = district name, A3 = region, A4 = population, A11 = average salary, A12 = unemployment rate 1995, A13 = unemployment rate 1996, A15 = number of crimes 1995, A16 = number of crimes 1996.

### Step 4: Import the CSV files into DBeaver

Import the tables in this exact order. The order matters because some tables reference others through foreign keys.

1. district (use `district_clean.csv`)
2. account
3. client
4. disp
5. loan
6. order
7. trans
8. card

**Import steps in DBeaver:**
1. Right-click the table name in the left panel
2. Select **Import Data**
3. Choose **CSV** as the source
4. Browse to the CSV file
5. Set the **delimiter** to semicolon `;`
6. Ensure **Header row** is ticked
7. Click Next through the column mapping screen and Finish

**If you encounter a batch insert error:** Go to the import settings and disable batch insert (set batch size to 1). This tells PostgreSQL to import row by row and skip any problematic rows rather than stopping entirely.

### Step 5: Verify the import

Run this in DBeaver to confirm row counts:

```sql
SELECT COUNT(*) FROM account;   -- Expected: 4,500
SELECT COUNT(*) FROM client;    -- Expected: 5,369
SELECT COUNT(*) FROM district;  -- Expected: 77
SELECT COUNT(*) FROM disp;      -- Expected: 5,369
SELECT COUNT(*) FROM loan;      -- Expected: 682
SELECT COUNT(*) FROM "order";   -- Expected: 6,471
SELECT COUNT(*) FROM trans;     -- Expected: 1,056,320
SELECT COUNT(*) FROM card;      -- Expected: 892
```

---

## SQL Queries

All three queries are in `Querying_the_Berka_Bank_Data.sql`. Below is a summary of each.

### Query 1: Balance Tier vs Default Rate

**Concept:** Splits all accounts into quintiles by average balance using NTILE(5), then compares the default rate of the top 20% against the bottom 20%.

**Key finding:** The bottom 20% default at 37.50% versus 2.85% for the top 20%. A 13x difference in risk driven by a single behavioural signal.

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

### Query 2: Month-Over-Month Velocity Drop

**Concept:** Uses the LAG() window function to compare each account's monthly transaction count against the previous month. Flags any account with a drop greater than 40%.

**Key finding:** Several accounts dropped 80-90% in a single month. December 1998 results are a data artefact caused by the dataset ending mid-month, not genuine risk signals.

### Query 3: Cash-Out Before Default Detection

**Concept:** Identifies accounts with a bad or troubled loan whose most recent transaction was a large outgoing payment relative to their average monthly income.

**Challenge encountered:** The first version used a correlated subquery to find the latest transaction per account. This executed once for every row in the trans table, meaning over one million individual subquery executions. The query ran for over one hour without completing and had to be cancelled.

**Fix:** Rewrote using ROW_NUMBER() window function, which processes all rows in a single pass. Runtime dropped from over one hour to under five seconds.

**Key finding:** At an 80% threshold, zero accounts are flagged. Lowering to 50% surfaces account 10857 as HIGH RISK: the largest troubled loan in the dataset (385,560) with a last transfer of 73.68% of average monthly income to another account.

---

## Challenges and How They Were Resolved

| Challenge | Cause | Resolution |
|---|---|---|
| district.csv import fails | Question marks used for missing values instead of NULL | Replaced with column mean in Python before importing |
| district table primary key mismatch | CSV column named A1, table expected district_id | Recreated district table using A1 as primary key to match CSV headers exactly |
| Batch insert error on import | One or more rows violating constraints | Disabled batch insert in DBeaver import settings |
| Query 3 ran for over one hour | Correlated subquery executing once per row across 1,056,320 rows | Rewrote using ROW_NUMBER() window function for single-pass processing |
| December 1998 flagged as high risk in Query 2 | Dataset ends mid-December 1998, causing low transaction counts in final month | Identified as a data artefact; in production would filter out the most recent month before flagging |

---

## Key Insights

**Query 1:** Average balance is a strong predictor of credit risk. The bottom 20% of accounts by average balance default at a rate 13 times higher than the top 20%. This validates average balance behaviour as a high-value feature in a credit scoring model.

**Query 2:** Sudden drops in transaction velocity are an early warning signal for default risk. Some accounts dropped 90% in a single month. Post-disbursement monitoring of transaction activity can give a credit team time to intervene before a payment is missed.

**Query 3:** The threshold at which a risk flag fires is a business decision, not a technical one. At 80% no accounts are flagged. At 50% one genuine high-risk account surfaces. This demonstrates the precision versus recall tradeoff that every credit team must navigate when tuning a risk model.

---

## Connect

- **GitHub:** [github.com/KathituCodes](https://github.com/KathituCodes)
- **Email:** peterkathitu@gmail.com
- **Dashboard:** [Live on Streamlit](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)
