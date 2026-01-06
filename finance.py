import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt

st.set_page_config(page_title="UPI Financial Analyzer", layout="wide")

st.title("💰 Personal UPI Usage and Financial Analyzer (LLM-Based)")
st.write("LLM-style NLP system to analyze UPI transactions and provide financial insights.")

uploaded_file = st.file_uploader("📄 Upload UPI PDF", type=["pdf"])

# ---------------- NLP UTILITIES ----------------
def extract_text_from_pdf(pdf):
    lines = []
    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split("\n"))
    return lines


def categorize(text):
    t = text.lower()

    if any(x in t for x in ["grocery", "vegetable", "milk", "ration", "supermarket"]):
        return "Grocery"
    if any(x in t for x in ["electricity", "water", "gas", "recharge", "bill", "rent"]):
        return "Bills"
    if any(x in t for x in ["swiggy", "zomato", "junk", "snacks", "restaurant"]):
        return "Food"
    if any(x in t for x in ["movie", "netflix", "spotify", "theatre", "entertainment"]):
        return "Entertainment"
    if any(x in t for x in ["amazon", "flipkart", "shopping", "store"]):
        return "Shopping"
    if any(x in t for x in ["uber", "ola", "cab", "travel"]):
        return "Travel"

    return "Others"


def llm_advice(summary, waste_count):
    highest = summary.idxmax()
    return f"""
### 🤖 AI Financial Recommendations
• Highest spending category: **{highest}**
• Identified **{waste_count}** avoidable expenses
• Cut down entertainment & impulse purchases
• Plan monthly budgets category-wise
• Target savings ≥ **20%** income
_(LLM-style reasoning output)_
"""


# ---------------- MAIN ----------------
if uploaded_file:
    st.success("PDF uploaded")

    raw = extract_text_from_pdf(uploaded_file)
    rows = [l for l in raw if re.search(r"(₹|\d+\.\d{2})", l)]

    if rows:
        df = pd.DataFrame(rows, columns=["Transaction"])
        df["Amount"] = df["Transaction"].str.extract(r"([\d,]+\.?\d*)")[0]
        df["Amount"] = df["Amount"].str.replace(",", "").astype(float)
        df["Category"] = df["Transaction"].apply(categorize)

        st.subheader("📄 Extracted Transactions")
        st.dataframe(df, use_container_width=True)

        summary = df.groupby("Category")["Amount"].sum()
        summary = summary[summary > 0]

        st.subheader("📊 Category-wise Spending")
        st.bar_chart(summary)

        # -------------- FIXED WASTEFUL LOGIC ----------------
        wasteful = df[
            (df["Category"] == "Entertainment") |
            ((df["Category"] == "Junk Food") & (df["Amount"] < 250)) |
            ((df["Category"] == "Shopping") & (df["Amount"] < 500))
        ]

        st.subheader("⚠️ Potential Wasteful Spending")
        if wasteful.empty:
            st.write("No wasteful spending detected")
        else:
            st.dataframe(wasteful, use_container_width=True)
            st.caption("Entertainment, junk food, and impulse shopping only")

        st.subheader("🤖 LLM-Based Insights")
        st.markdown(llm_advice(summary, len(wasteful)))

    else:
        st.error("No transactions detected in PDF")

else:
    st.info("Upload UPI PDF to begin analysis")
