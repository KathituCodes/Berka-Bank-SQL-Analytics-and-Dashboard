"""
Berka Bank SQL Analytics Dashboard
Author : Urbanus Kathitu | Kat.Codes
GitHub : github.com/KathituCodes/Berka-Bank-SQL-Analytics-and-Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Berka Bank SQL Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY   = "#1F3864"
TEAL   = "#2E75B6"
RED    = "#C00000"
GREEN  = "#375623"
ORANGE = "#E97132"

st.markdown(f"""
<style>
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {NAVY} 0%, #162a50 100%);
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {{
        color: #E8EEF7 !important;
    }}
    [data-testid="metric-container"] {{
        background-color: transparent;
        border: 1px solid rgba(46, 117, 182, 0.3);
        border-left: 4px solid {TEAL};
        border-radius: 8px;
        padding: 12px 16px;
    }}
    .section-header {{
        background: linear-gradient(90deg, {NAVY}, {TEAL});
        color: white !important;
        padding: 10px 18px;
        border-radius: 6px;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 16px;
        letter-spacing: 0.2px;
    }}
    .insight-box {{
        background-color: #EBF3FB;
        border-left: 4px solid {TEAL};
        border-radius: 6px;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: 14px;
        color: #1a2e4a !important;
        line-height: 1.6;
    }}
    .warning-box {{
        background-color: #FFF3E0;
        border-left: 4px solid {ORANGE};
        border-radius: 6px;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: 14px;
        color: #5a3000 !important;
        line-height: 1.6;
    }}
    .risk-box {{
        background-color: #FFE5E5;
        border-left: 4px solid {RED};
        border-radius: 6px;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: 14px;
        color: #7a0000 !important;
        line-height: 1.6;
    }}
    .query-card {{
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 8px;
        padding: 16px;
        min-height: 150px;
    }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)


# SESSION STATE
if "page" not in st.session_state:
    st.session_state.page = "Overview"

def set_page(p):
    st.session_state.page = p


# DATA LOADING
@st.cache_data
def load_data():
    data_dir = os.path.join(os.path.dirname(__file__), "data")

    def read(filename):
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            st.error(f"Missing file: data/{filename}")
            st.stop()
        return pd.read_csv(path)

    return (
        read("query1_balance_vs_default.csv"),
        read("query2_velocity_drop.csv"),
        read("query3_cashout_risk_50%.csv"),
        read("query3_cashout_risk_80%.csv"),
    )

q1, q2, q3, q4 = load_data()


# CHART LAYOUT HELPER
# Forces dark text on white background — readable in both light and dark mode
def chart_layout(height=360, **kwargs):
    dark = "#1A1A1A"

    # Force dark text on every axis passed in kwargs
    for axis_key in ["xaxis", "yaxis"]:
        if axis_key in kwargs:
            ax = kwargs[axis_key]
            ax.setdefault("color",       dark)
            ax.setdefault("tickfont",    dict(color=dark, size=12))
            ax.setdefault("title_font",  dict(color=dark, size=13))
            ax.setdefault("gridcolor",   "#E8E8E8")
            ax.setdefault("linecolor",   "#CCCCCC")
            kwargs[axis_key] = ax

    base = dict(
        height=height,
        margin=dict(t=30, b=40, l=60, r=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=dark, family="Arial, sans-serif", size=12),
        showlegend=False,
    )
    base.update(kwargs)
    return base


def legend_style():
    return dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        font=dict(color="#1A1A1A", size=12),
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#E0E0E0",
        borderwidth=1
    )


# SIDEBAR
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:16px 0 12px 0;'>
        <div style='font-size:36px;'>🏦</div>
        <div style='color:white; font-size:17px; font-weight:800;
                    margin-top:8px; letter-spacing:0.3px;'>
            Berka Bank Analytics
        </div>
        <div style='color:#90CAF9; font-size:11px; margin-top:4px;'>
            Urbanus Kathitu | Kat.Codes
        </div>
    </div>
    <hr style='border-color:rgba(46,117,182,0.4); margin:8px 0 16px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("<p style='color:#90CAF9; font-size:11px; font-weight:700; "
                "letter-spacing:1px; margin-bottom:8px;'>NAVIGATE</p>",
                unsafe_allow_html=True)

    pages = [
        ("🏠 Overview",                    "Overview"),
        ("📊 Query 1: Balance vs Default", "Query 1: Balance vs Default"),
        ("📉 Query 2: Velocity Drop",      "Query 2: Velocity Drop"),
        ("⚠️ Query 3: Cash-Out Risk",      "Query 3: Cash-Out Risk"),
    ]

    for label, key in pages:
        active = st.session_state.page == key
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            set_page(key)
            st.rerun()

    st.markdown("<hr style='border-color:rgba(46,117,182,0.4); margin:16px 0;'>",
                unsafe_allow_html=True)

    st.markdown(f"""
    <div style='color:#90CAF9; font-size:11px; line-height:1.9;'>
        <p style='color:white; font-size:12px; font-weight:700;
                  margin-bottom:6px; letter-spacing:0.5px;'>DATASET</p>
        Czech Bank 1993–1998<br>
        1,056,320 transactions<br>
        682 loans | 4,500 accounts<br><br>
        <p style='color:white; font-size:12px; font-weight:700;
                  margin-bottom:6px; letter-spacing:0.5px;'>SQL TECHNIQUES</p>
        CTEs | Window Functions<br>
        NTILE | LAG | ROW_NUMBER<br>
        Subqueries | Aggregations<br><br>
        <p style='color:white; font-size:12px; font-weight:700;
                  margin-bottom:6px; letter-spacing:0.5px;'>STACK</p>
        PostgreSQL | DBeaver<br>
        Python | Streamlit | Plotly
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════
page = st.session_state.page

if page == "Overview":

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {NAVY} 0%, {TEAL} 100%);
                padding: 32px 28px; border-radius: 12px; margin-bottom: 28px;
                box-shadow: 0 4px 16px rgba(31,56,100,0.2);'>
        <h1 style='color:white; margin:0; font-size:26px; font-weight:800;'>
            Berka Bank — Transaction-Level SQL Analytics
        </h1>
        <p style='color:#BBDEFB; margin:10px 0 0 0; font-size:14px; line-height:1.6;'>
            Credit risk insights extracted from 1,056,320 real bank transactions
            using advanced PostgreSQL: CTEs, Window Functions, and Subqueries.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Transactions", "1,056,320")
    c2.metric("Total Accounts",     "4,500")
    c3.metric("Total Loans",        "682")
    c4.metric("Bad Loans (B+D)",    "76",   delta="-11.1% of total", delta_color="inverse")
    c5.metric("Good Loans (A+C)",   "606",  delta="88.9% of total")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">Loan Status Distribution</div>',
                    unsafe_allow_html=True)
        status_df = pd.DataFrame({
            "Status": ["C: Running, Good", "A: Finished, Paid",
                       "D: Running, In Trouble", "B: Finished, Unpaid"],
            "Count":  [403, 203, 45, 31]
        })
        fig = go.Figure(go.Bar(
            x=status_df["Status"], y=status_df["Count"],
            marker_color=[GREEN, TEAL, ORANGE, RED],
            text=status_df["Count"], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
        ))
        fig.update_layout(**chart_layout(
            showlegend=False,
            xaxis=dict(tickangle=-15, title=""),
            yaxis=dict(title="Number of Loans")
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Good vs Bad Loan Split</div>',
                    unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=["Good (A+C)", "Bad (B+D)"],
            values=[606, 76],
            marker_colors=[TEAL, RED],
            hole=0.55, textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
        ))
        fig2.update_layout(**chart_layout(
            annotations=[dict(text="682<br>Loans", x=0.5, y=0.5,
                              font_size=16, font_color=NAVY, showarrow=False)]
        ))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <b>Core Credit Risk Question:</b> Out of 682 loans, 76 are bad or in trouble.
        How do you identify these 76 before disbursing the money?
        The three queries below explore different behavioural signals that predict this outcome.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Project Queries at a Glance</div>',
                unsafe_allow_html=True)

    ca, cb, cc = st.columns(3)
    with ca:
        st.markdown(f"""
        <div class="query-card" style='border-top:4px solid {TEAL};
             background:white; color:{NAVY};'>
            <b style='font-size:15px;'>📊 Query 1: Balance vs Default</b><br><br>
            <span style='color:#333; font-size:13px;'>
                Bottom 20% accounts default at <b>37.5%</b> vs <b>2.85%</b>
                for the top 20%. A <b>13x</b> difference in risk.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with cb:
        st.markdown(f"""
        <div class="query-card" style='border-top:4px solid {ORANGE};
             background:white; color:{NAVY};'>
            <b style='font-size:15px;'>📉 Query 2: Velocity Drop</b><br><br>
            <span style='color:#333; font-size:13px;'>
                Flagged accounts whose monthly transactions dropped more than
                <b>40%</b> in a single month. Worst case: <b>-90%</b>.
            </span>
        </div>
        """, unsafe_allow_html=True)
    with cc:
        st.markdown(f"""
        <div class="query-card" style='border-top:4px solid {RED};
             background:white; color:{NAVY};'>
            <b style='font-size:15px;'>⚠️ Query 3: Cash-Out Risk</b><br><br>
            <span style='color:#333; font-size:13px;'>
                Account <b>10857</b> flagged HIGH RISK: largest troubled loan
                (385,560) with last transfer of <b>73.68%</b> of monthly income.
            </span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PAGE: QUERY 1
# ═══════════════════════════════════════════════════════════
elif page == "Query 1: Balance vs Default":

    st.markdown(f"<h2 style='color:{NAVY};'>Query 1: Does Account Balance Predict Default Risk?</h2>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <b>Business Question:</b> If a customer maintains a consistently high average balance,
        are they less likely to default on a loan? I split all 4,500 accounts into quintiles
        by average balance across all 1,056,320 transactions and compared the default rate
        of the top 20% against the bottom 20%.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    bottom_row = q1[q1["balance_tier"] == "BOTTOM 20%"].iloc[0]
    top_row    = q1[q1["balance_tier"] == "TOP 20%"].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bottom 20% Default Rate", f"{bottom_row['default_rate_percent']}%",
              delta="High risk", delta_color="inverse")
    c2.metric("Top 20% Default Rate",    f"{top_row['default_rate_percent']}%",
              delta="Low risk")
    c3.metric("Risk Multiplier", "13x",  delta="Bottom defaults 13x more")
    c4.metric("Total Loans in Comparison",
              int(bottom_row["total_loans"] + top_row["total_loans"]))

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">Default Rate by Balance Tier</div>',
                    unsafe_allow_html=True)
        bar_colors = [RED if t == "BOTTOM 20%" else GREEN for t in q1["balance_tier"]]
        fig = go.Figure(go.Bar(
            x=q1["balance_tier"], y=q1["default_rate_percent"],
            marker_color=bar_colors,
            text=[f"{v}%" for v in q1["default_rate_percent"]],
            textposition="outside", width=0.4,
            hovertemplate="<b>%{x}</b><br>Default Rate: %{y}%<extra></extra>"
        ))
        fig.update_layout(**chart_layout(
            showlegend=False,
            xaxis=dict(title="Balance Tier"),
            yaxis=dict(title="Default Rate (%)", range=[0, 45])
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Loan Volume: Good vs Bad by Tier</div>',
                    unsafe_allow_html=True)
        q1["good_loans"] = q1["total_loans"] - q1["bad_loans"]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Good Loans", x=q1["balance_tier"],
                              y=q1["good_loans"], marker_color=TEAL))
        fig2.add_trace(go.Bar(name="Bad Loans",  x=q1["balance_tier"],
                              y=q1["bad_loans"],  marker_color=RED))
        fig2.update_layout(**chart_layout(
            barmode="stack", showlegend=True,
            legend=legend_style(),
            xaxis=dict(title="Balance Tier"),
            yaxis=dict(title="Number of Loans")
        ))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Query Results</div>', unsafe_allow_html=True)
    st.dataframe(q1[["balance_tier", "total_loans", "bad_loans", "default_rate_percent"]],
                 use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="insight-box">
        <b>Key Insight:</b> Lending to someone in the bottom 20% by average balance carries a
        37.5% default rate compared to just 2.85% for the top 20%. That is a 13x difference
        in risk driven by a single behavioural signal.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
        <b>SQL Technique:</b> Three chained CTEs. CTE 1 calculates average balance per account.
        CTE 2 uses NTILE(5) to split accounts into five groups by balance.
        CTE 3 filters to top and bottom groups. Final SELECT joins to loan table.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PAGE: QUERY 2
# ═══════════════════════════════════════════════════════════
elif page == "Query 2: Velocity Drop":

    st.markdown(f"<h2 style='color:{NAVY};'>Query 2: Month-Over-Month Transaction Velocity Drop</h2>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <b>Business Question:</b> Can we detect early warning signs of default by monitoring
        sudden drops in transaction activity? I flagged every account whose monthly transaction
        count dropped more than 40% compared to the previous month using LAG().
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accounts Flagged", len(q2))
    c2.metric("Worst Drop",       f"{q2['pct_change'].min()}%")
    c3.metric("Average Drop",     f"{q2['pct_change'].mean():.1f}%")
    c4.metric("All Flags",        "HIGH RISK > 40%")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">Transaction Drop % per Flagged Account</div>',
                    unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=q2["account_id"].astype(str), y=q2["pct_change"],
            marker_color=RED,
            text=[f"{v}%" for v in q2["pct_change"]], textposition="outside",
            hovertemplate="<b>Account %{x}</b><br>Drop: %{y}%<extra></extra>"
        ))
        fig.add_hline(y=-40, line_dash="dash", line_color=ORANGE,
                      annotation_text="40% Threshold",
                      annotation_position="top right")
        fig.update_layout(**chart_layout(
            showlegend=False,
            xaxis=dict(title="Account ID", tickangle=-45),
            yaxis=dict(title="% Change in Monthly Transactions", range=[-100, 0])
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Flagged Accounts by Year</div>',
                    unsafe_allow_html=True)
        year_counts = q2.groupby("txn_year").size().reset_index(name="flagged_accounts")
        fig2 = go.Figure(go.Bar(
            x=year_counts["txn_year"].astype(str),
            y=year_counts["flagged_accounts"],
            marker_color=TEAL,
            text=year_counts["flagged_accounts"], textposition="outside",
            hovertemplate="<b>Year %{x}</b><br>Flagged: %{y}<extra></extra>"
        ))
        fig2.update_layout(**chart_layout(
            showlegend=False,
            xaxis=dict(title="Year"),
            yaxis=dict(title="Number of Flagged Accounts")
        ))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Previous Month vs Current Month Transaction Count</div>',
                unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=q2["account_id"].astype(str), y=q2["previous_month_txns"],
        mode="markers+lines", name="Previous Month",
        marker=dict(color=GREEN, size=9), line=dict(color=GREEN, dash="dot")
    ))
    fig3.add_trace(go.Scatter(
        x=q2["account_id"].astype(str), y=q2["current_month_txns"],
        mode="markers+lines", name="Current Month (After Drop)",
        marker=dict(color=RED, size=9), line=dict(color=RED)
    ))
    fig3.update_layout(**chart_layout(
        height=300, showlegend=True,
        legend=legend_style(),
        xaxis=dict(title="Account ID", tickangle=-45),
        yaxis=dict(title="Transaction Count")
    ))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-header">Query Results</div>', unsafe_allow_html=True)
    st.dataframe(q2, use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="warning-box">
        <b>Important Observation:</b> December 1998 appears repeatedly in the results.
        This is a data collection artefact, not a genuine risk signal. The dataset ends
        in late 1998, so many accounts have fewer transactions in their final recorded month.
        In production I would filter out the most recent month before flagging risk.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <b>SQL Technique:</b> LAG() window function partitioned by account_id and ordered
        chronologically. Processes all 1,056,320 rows in a single pass with no loops.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# PAGE: QUERY 3
# ═══════════════════════════════════════════════════════════
elif page == "Query 3: Cash-Out Risk":

    st.markdown(f"<h2 style='color:{NAVY};'>Query 3: Cash-Out Before Default Risk Detection</h2>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <b>Business Question:</b> Can we detect accounts that are deliberately withdrawing
        funds before defaulting on a loan? I searched for accounts with a bad or troubled loan
        whose most recent transaction was a large outgoing payment relative to average monthly
        income. I ran this query at two different thresholds to observe how sensitivity changes.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Select Risk Threshold</div>',
                unsafe_allow_html=True)

    threshold = st.radio(
        "Withdrawal threshold as % of average monthly inflow:",
        options=["50% Threshold — catches HIGH RISK accounts",
                 "80% Threshold — all accounts show as MONITOR"],
        horizontal=True
    )

    active_df     = q3 if "50%" in threshold else q4
    threshold_val = 50  if "50%" in threshold else 80
    t_label       = "50%" if "50%" in threshold else "80%"

    high_risk_count = len(active_df[
        active_df["risk_flag"] == "HIGH RISK: Large withdrawal on bad loan account"
    ])
    monitor_count = len(active_df[active_df["risk_flag"] == "MONITOR"])

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accounts Analysed", len(active_df))
    c2.metric("HIGH RISK Flags",   high_risk_count,
              delta="Flagged for review" if high_risk_count > 0 else "None flagged",
              delta_color="inverse" if high_risk_count > 0 else "normal")
    c3.metric("MONITOR",           monitor_count)
    c4.metric("Active Threshold",  f"{t_label} of avg inflow")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown(f'<div class="section-header">Withdrawal % of Avg Inflow (Threshold: {t_label})</div>',
                    unsafe_allow_html=True)
        bar_colors = [
            RED if r == "HIGH RISK: Large withdrawal on bad loan account" else TEAL
            for r in active_df["risk_flag"]
        ]
        fig = go.Figure(go.Bar(
            x=active_df["account_id"].astype(str),
            y=active_df["withdrawal_as_pct_of_income"],
            marker_color=bar_colors,
            text=[f"{v}%" for v in active_df["withdrawal_as_pct_of_income"]],
            textposition="outside",
            hovertemplate="<b>Account %{x}</b><br>Withdrawal: %{y}%<extra></extra>"
        ))
        fig.add_hline(y=threshold_val, line_dash="dash", line_color=ORANGE,
                      annotation_text=f"{t_label} Threshold",
                      annotation_position="top right")
        fig.update_layout(**chart_layout(
            showlegend=False,
            xaxis=dict(title="Account ID", tickangle=-30),
            yaxis=dict(title="Withdrawal as % of Avg Monthly Inflow", range=[0, 85])
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Risk Flag Distribution</div>',
                    unsafe_allow_html=True)
        flag_counts = active_df["risk_flag"].value_counts().reset_index()
        flag_counts.columns = ["Risk Flag", "Count"]
        pie_colors = [RED if "HIGH RISK" in f else GREEN for f in flag_counts["Risk Flag"]]
        fig2 = go.Figure(go.Pie(
            labels=flag_counts["Risk Flag"], values=flag_counts["Count"],
            marker_colors=pie_colors, hole=0.5, textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
        ))
        fig2.update_layout(**chart_layout(showlegend=False))
        st.plotly_chart(fig2, use_container_width=True)

    # Scatter chart — clean single initialization, no duplicate loop
    st.markdown('<div class="section-header">Loan Amount vs Last Transaction Amount</div>',
                unsafe_allow_html=True)
    fig3 = go.Figure()
    for status, symbol, label in [
        ("D", "diamond", "Status D: Running, In Trouble"),
        ("B", "circle",  "Status B: Finished, Unpaid")
    ]:
        subset = active_df[active_df["loan_status"] == status]
        if subset.empty:
            continue
        s_colors = [
            RED if r == "HIGH RISK: Large withdrawal on bad loan account" else TEAL
            for r in subset["risk_flag"]
        ]
        fig3.add_trace(go.Scatter(
            x=subset["loan_amount"], y=subset["last_txn_amount"],
            mode="markers", name=label,
            marker=dict(color=s_colors, size=14, symbol=symbol,
                        line=dict(width=1, color="white")),
            text=subset["account_id"].astype(str),
            hovertemplate=("<b>Account %{text}</b><br>"
                           "Loan: %{x:,.0f}<br>"
                           "Last Txn: %{y:,.0f}<extra></extra>")
        ))
    fig3.update_layout(**chart_layout(
        height=320, showlegend=True,
        legend=legend_style(),
        xaxis=dict(title="Loan Amount"),
        yaxis=dict(title="Last Transaction Amount")
    ))
    st.plotly_chart(fig3, use_container_width=True)

    # Threshold comparison table
    st.markdown('<div class="section-header">Threshold Comparison: 50% vs 80%</div>',
                unsafe_allow_html=True)

    comparison = q3[["account_id", "loan_amount", "loan_status",
                      "withdrawal_as_pct_of_income"]].copy()
    comparison["Risk @ 80%"] = q4["risk_flag"].apply(
        lambda x: "HIGH RISK" if "HIGH RISK" in str(x) else "MONITOR")
    comparison["Risk @ 50%"] = q3["risk_flag"].apply(
        lambda x: "HIGH RISK" if "HIGH RISK" in str(x) else "MONITOR")
    comparison = comparison.rename(columns={
        "account_id":                  "Account ID",
        "loan_amount":                 "Loan Amount",
        "loan_status":                 "Loan Status",
        "withdrawal_as_pct_of_income": "Withdrawal % of Inflow"
    })

    def highlight_risk(val):
        if val == "HIGH RISK":
            return "background-color: #FFE5E5; color: #C00000; font-weight: bold;"
        elif val == "MONITOR":
            return "background-color: #E8F5E9; color: #375623;"
        return ""

    st.dataframe(
        comparison.style.map(highlight_risk, subset=["Risk @ 80%", "Risk @ 50%"]),
        use_container_width=True, hide_index=True
    )

    st.markdown("""
    <div class="risk-box">
        <b>Key Finding:</b> At an 80% threshold zero accounts are flagged. Lowering to 50%
        surfaces account 10857 as HIGH RISK: the largest troubled loan in the dataset (385,560)
        with a last transfer of 6,426 representing 73.68% of average monthly income.
        The transfer went to another account, suggesting deliberate fund movement before default.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
        <b>Precision vs Recall Tradeoff:</b> A high threshold catches fewer accounts but misses
        real risks. A low threshold catches more but may flag good customers incorrectly.
        The right threshold is a business decision the data scientist informs but does not
        make alone.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        <b>SQL Technique:</b> ROW_NUMBER() window function partitioned by account_id and
        ordered by date descending. The original correlated subquery ran for over one hour
        on 1,056,320 rows. ROW_NUMBER() reduced runtime to under 5 seconds.
    </div>
    """, unsafe_allow_html=True)
