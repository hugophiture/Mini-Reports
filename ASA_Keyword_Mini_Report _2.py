# MAIN.py  ── mini-dashboard for “worst” ASA keywords
# Run with:  streamlit run MAIN.py

import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

DATA_FILE = Path("/Users/hugodelgado/Desktop/Keywords_Folder/your_keywords_file.csv")

# ── FUNCTIONS ────────────In here you will create the logic of your dashboard  for this example is the Worst Performers of ASA Keywords base on CPI and CVR─────────────────────────────────────
@st.cache_data
def load_and_score(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # High CPI + low CVR  → worst_score
    df["CPI_norm"] = (df["CPI"] - df["CPI"].min()) / (df["CPI"].max() - df["CPI"].min())
    df["CVR_inv_norm"] = (df["CVR"].max() - df["CVR"]) / (df["CVR"].max() - df["CVR"].min())
    df["worst_score"] = (df["CPI_norm"] + df["CVR_inv_norm"]) / 2
    df["worst_rank_country"] = (
        df.groupby("Country")["worst_score"].rank(method="first", ascending=False)
    )
    return df

# ── UI  ────────────────────────────────────────── > you woll dseign your own UI Dashboard. In this example is a simple dashboard with a selectbox to select the country and a scatter plot with the worst keywords.
st.set_page_config(page_title="ASA Keyword Mini-Report", layout="wide")
st.title("Worst-Performing ASA Keywords")

df = load_and_score(DATA_FILE)

# Country selector
country = st.selectbox("Select a country", sorted(df["Country"].unique()))

# Filter & Top-10
country_df = df[df["Country"] == country]
top10 = (
    country_df.sort_values("worst_score", ascending=False)
    .head(10) # You can change the number of keywords you want to show 20 or 50
    .reset_index(drop=True)
)

# Show table
st.subheader(f"Top 10 worst keywords in {country}")
st.dataframe(top10[["keyword", "CPI", "CVR", "worst_score"]])

# Scatter plot (all points, highlight Top-10)
fig = px.scatter(
    country_df, x="CPI", y="CVR",
    hover_data=["keyword"],
    title=f"CVR vs CPI — {country}",
    height=600
)
fig.add_scatter(
    x=top10["CPI"], y=top10["CVR"],
    mode="markers+text",
    marker=dict(symbol="x", size=13, color="red"),
    text=top10["keyword"],
    textposition="top center",
    name="Top 10 worst"
)
st.plotly_chart(fig, use_container_width=True)

# Optional CSV download
csv_bytes = top10.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Top-10 as CSV", csv_bytes, file_name=f"Top10_{country}.csv"
)
