# Berka Bank SQL Analytics and Dashboard

## Live Dashboard

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)

**[View the live dashboard here](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)**

---

## Summary

Banks lend money, and some borrowers do not pay it back. The hard part is spotting the risky borrowers early. This project uses real records from a Czech bank (1993 to 1998), covering over one million transactions, to test three simple ideas for spotting risk:

1. Do customers who usually keep more money in their account fail to repay loans less often?
2. Does a sudden drop in account activity warn that a borrower is in trouble?
3. Can we spot a borrower pulling out their money just before they stop repaying?

I answered these by writing questions (called queries) in a database language called SQL. I then turned the results into an interactive dashboard that anyone can open in a web browser.

---

## Words Used in This Project

| Term | What it means |
|---|---|
| Query | A question written in SQL and asked of a database. The database replies with a table of results. |
| Default | When a borrower does not repay a loan as agreed. |
| Default rate | The share of loans that go bad. If 10 out of 100 loans go bad, the default rate is 10%. |
| Average balance | The typical amount of money sitting in an account over time. |
| Inflow | Money coming into an account, such as salary or deposits. |
| Threshold | A cut-off number. Anything above it gets flagged for a closer look. |
| Flag | A warning marker placed on an account so a person can review it. |

---

## The Three Questions

| Query | The question in plain words | SQL technique used (for technical readers) |
|---|---|---|
| 1 | Do customers with high balances default less on loans? | CTEs + NTILE window function |
| 2 | Does a drop in account activity signal default risk? | CTEs + LAG window function |
| 3 | Can we detect money being pulled out before default? | CTEs + ROW_NUMBER window function |

---

## The Data

The Berka dataset holds real financial records from a Czech bank. It is made up of eight linked tables, a bit like eight connected spreadsheets that follow a customer from signing up to repaying a loan.

| Table | Rows | What it holds |
|---|---|---|
| account | 4,500 | Every bank account |
| client | 5,369 | Every customer |
| district | 77 | Regional facts such as population and average salary |
| disp | 5,369 | The link between each customer and their account |
| loan | 682 | Every loan issued, including how it ended |
| order | 6,471 | Standing payment instructions, such as monthly rent |
| trans | 1,056,320 | Every single transaction |
| card | 892 | Credit cards issued |

**Download:** [Kaggle: The Berka Dataset](https://www.kaggle.com/datasets/marceloventura/the-berka-dataset)

---

## Tools Used

| Tool | What I used it for |
|---|---|
| PostgreSQL | The database that stores the data and answers the queries |
| DBeaver | The program used to write queries and load data into the database |
| Python (pandas, numpy) in Google Colab | Cleaning a small problem in the raw data |
| Python, Streamlit, Plotly | Building the interactive dashboard |
| Git and GitHub | Saving and sharing the project |

---

## What Is in This Repository

```
├── berka_dashboard.py               # The dashboard application
├── requirements.txt                 # List of Python tools the dashboard needs
├── README.md                        # This file
├── Querying_the_Berka_Bank_Data.sql # All three SQL queries, with notes
├── Handling_district_missing_values.ipynb  # Notebook that fixes the missing data
└── data/
    ├── query1_balance_vs_default.csv
    ├── query2_velocity_drop.csv
    ├── query3_cashout_risk_50%.csv
    └── query4_cashout_risk_80%.csv
```

The four files in the `data` folder are the saved results of the queries. The dashboard reads them to draw its charts. The last two files are the results of Query 3 run with two different cut-offs (50% and 80%).

---

## What I Found

**Query 1: Customers who keep more money in their account default far less.**
Accounts in the lowest 20% by average balance defaulted at a rate about 13 times higher than accounts in the highest 20%. This makes average balance a strong candidate for use in a credit scoring model.

**Query 2: A sudden fall in activity can be an early warning.**
Some accounts dropped 90% in the number of transactions in a single month. Watching for this after a loan is paid out can give a lender time to step in before a payment is missed.

**Query 3: The cut-off you choose decides who gets flagged.**
At an 80% cut-off, no accounts were flagged. At 50%, one account was flagged as high risk. Choosing the cut-off is a business decision, not a technical one. A strict cut-off misses some real risks. A loose cut-off flags good customers by mistake. Every credit team has to balance the two. In data science this trade-off is called precision versus recall.

---

## The Three Questions in More Detail

### Query 1: Do customers with higher balances default less?

**How I answered it**

1. I worked out the average balance of every account across all its transactions.
2. I ranked all accounts from lowest to highest average balance and split them into five equal groups.
3. I kept only the lowest 20% and the highest 20%, so the comparison would be clear.
4. I linked these accounts to the loan records and calculated what share of loans went bad in each group. A loan counts as bad if it ended unpaid or is currently in trouble (statuses B or D).

**Result**

| Group | Default rate |
|---|---|
| Lowest 20% by balance | 37.50% |
| Highest 20% by balance | 2.85% |

That is roughly a 13 times difference, based on one everyday habit.

**The SQL** (for technical readers)

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

### Query 2: Does a sudden drop in activity signal trouble?

**How I answered it**

1. I counted each account's transactions per month.
2. For every account and month, I looked back at the previous month's count.
3. I calculated the percentage change and flagged any drop larger than 40%.

**Result**

Several accounts dropped 80% to 90% in a single month. Results for December 1998 kept appearing, but they are a false alarm. The dataset ends partway through that month, so accounts look quiet only because the records stopped early. In a real setting, I would leave out the most recent month before flagging anyone.

*Technical note: this query uses the LAG() window function to place each account's previous month next to the current month.*

### Query 3: Can we spot money being pulled out before default?

**What I looked for**

Accounts meeting both of these conditions at the same time:

- The account has a bad or troubled loan.
- The most recent transaction was a large payment out, bigger than a set share (first 80%, then 50%) of the account's average monthly income.

Either condition alone is not a strong warning. Together, they may point to money being moved out on purpose.

**A problem I ran into**

My first version found each account's latest transaction by checking the whole table again for every single row. With over a million rows, that meant over a million separate checks. It ran for more than an hour and I had to cancel it.

I rewrote it so the database ranks each account's transactions from newest to oldest in one pass, then keeps only the newest. This ran in under five seconds. A query that gives the right answer but takes an hour is not ready for real use.

**Result**

At an 80% cut-off, no accounts were flagged. At 50%, account 10857 was flagged as high risk. It has the largest loan among the eight troubled accounts reviewed (385,560), and its last transaction was a transfer to another account worth 73.68% of its average monthly income.

*Technical note: this query uses the ROW_NUMBER() window function to find each account's latest transaction.*

---

## Problems I Ran Into and How I Fixed Them

| Problem | What caused it | How I fixed it |
|---|---|---|
| The district file would not load | Missing values were written as question marks instead of being left empty | Replaced the question marks with the column average using Python, before loading |
| The district table did not match the file | The file's first column is named A1, but my table expected a different name | Recreated the district table using A1, so it matches the file exactly |
| An error appeared during loading | One or more rows broke the table's rules | Turned off batch loading in DBeaver so rows load one at a time |
| Query 3 ran for over an hour | It repeated a search once for each of the 1,056,320 rows | Rewrote it to rank all rows in a single pass |
| December 1998 looked high risk in Query 2 | The dataset ends partway through December 1998, so that month has fewer transactions | Recognised it as a data issue. In real use, I would leave out the most recent month |

---

## How to Run This Project

There are three levels, depending on how much you want to do.

### Option 1: Just look at the results

Open the [live dashboard](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/). Nothing to install.

### Option 2: Run the dashboard on your own computer

You need Python 3.8 or higher. You do not need PostgreSQL for this option, because the dashboard reads the saved results in the `data` folder.

```bash
git clone https://github.com/KathituCodes/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
streamlit run berka_dashboard.py
```

### Option 3: Rebuild the database and re-run the queries

You need Python 3.8 or higher, PostgreSQL, and DBeaver (or any PostgreSQL client). Follow the steps below.

---

## Rebuilding the Database (Technical Steps)

### Step 1: Download and inspect the raw files

Download the eight CSV files from Kaggle. Three things to know about them:

- They use a **semicolon (`;`)** to separate values, not a comma.
- Dates are stored as `YYMMDD` codes (for example, 980315), not as normal dates.
- The text is in Czech. Key terms are translated below.

| Czech term | English meaning |
|---|---|
| PRIJEM | Credit (money coming in) |
| VYDAJ | Debit (money going out) |
| VYBER | Cash withdrawal |
| VKLAD | Cash deposit |
| PREVOD NA UCET | Transfer to another account |
| PREVOD Z UCTU | Transfer from another account |
| VYBER KARTOU | Credit card withdrawal |

### Step 2: Fix the missing values in the district file

The `district.csv` file has question marks (`?`) in two columns, **A12** and **A15**, where values are missing. PostgreSQL cannot load a question mark into a numeric column and shows this error:

```
Can't parse numeric value [?] using formatter
Invalid argument: Character ? is neither a decimal digit number,
decimal point, nor "e" notation exponential mark.
```

**Step 2a: Find the missing values (Python, in Google Colab or locally)**

```python
import pandas as pd

# Read the file, treating ? as a missing value
df = pd.read_csv('district.csv', sep=';', na_values=['?'])

# Confirm which columns have missing values
print("Missing values per column:")
print(df.isnull().sum())
# Output: A12 has 1 missing value, A15 has 1 missing value

# Check the affected rows
print(df[df.isnull().any(axis=1)])
```

**Why I chose to fill them with the column average:** The missing data is regional information, not transaction data, so it does not affect the transaction queries. Filling with the average is quick, keeps the overall pattern of the data, and avoids deleting a row.

**Step 2b: Fill the missing values and save a clean file**

```python
# Fill missing values with the column average
df['A12'] = df['A12'].fillna(df['A12'].mean())
df['A15'] = df['A15'].fillna(df['A15'].mean())

# Verify no missing values remain
print("Missing values after cleaning:")
print(df.isnull().sum())
# All columns should now show 0

# Save the cleaned file
df.to_csv('district_clean.csv', sep=';', index=False)
print("Clean file saved successfully")
```

Use `district_clean.csv` for all later imports. Do not import the original `district.csv` into PostgreSQL.

### Step 3: Create the database tables

Open DBeaver, connect to your PostgreSQL database, open a new SQL script, and run the following. This creates eight empty tables, one for each file.

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

> **A note on the district table:** The column names A1 to A16 match the file's headers exactly. After loading, A1 is the district ID. The main columns mean: A2 = district name, A3 = region, A4 = population, A11 = average salary, A12 = unemployment rate 1995, A13 = unemployment rate 1996, A15 = number of crimes 1995, A16 = number of crimes 1996.

### Step 4: Load the CSV files into DBeaver

Load the tables in this exact order. Some tables refer to others, so the tables they refer to must be loaded first.

1. district (use `district_clean.csv`)
2. account
3. client
4. disp
5. loan
6. order
7. trans
8. card

**How to load each file in DBeaver**

1. Right-click the table name in the left panel.
2. Select **Import Data**.
3. Choose **CSV** as the source.
4. Browse to the CSV file.
5. Set the **delimiter** to a semicolon `;`.
6. Make sure **Header row** is ticked.
7. Click Next through the column mapping screen, then Finish.

**If you get a batch insert error:** Open the import settings and turn off batch insert (set the batch size to 1). PostgreSQL will then load one row at a time and skip any problem rows instead of stopping completely.

### Step 5: Check that the loading worked

Run this in DBeaver to confirm each table has the right number of rows:

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

Once the counts match, open `Querying_the_Berka_Bank_Data.sql` and run the three queries.

---

## Connect

- **GitHub:** [github.com/KathituCodes](https://github.com/KathituCodes)
- **Email:** peterkathitu@gmail.com
- **Dashboard:** [Live on Streamlit](https://sql-analytics-with-app-dashboard-on-the-berka-bank-dataset-vwb.streamlit.app/)
