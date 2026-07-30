import streamlit as st
import pandas as pd
import io
import os

@st.cache_data(show_spinner=False)
def count_rows(file_bytes):
    return sum(1 for _ in io.BytesIO(file_bytes).readlines()) - 1

@st.cache_data(show_spinner=False)
def load_preview(file_bytes, file_name, nrows=1000):
    try:
        return pd.read_csv(io.BytesIO(file_bytes), nrows=nrows, low_memory=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(io.BytesIO(file_bytes), nrows=nrows, low_memory=False, encoding="latin-1")

@st.cache_data(show_spinner="Loading full dataset...")
def load_full(file_bytes, file_name):
    try:
        return pd.read_csv(io.BytesIO(file_bytes), low_memory=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(io.BytesIO(file_bytes), low_memory=False, encoding="latin-1")

@st.cache_data(show_spinner=False)
def make_download_bytes(file_bytes, file_name, selected_cols, keep_all, num_rows):
    if keep_all:
        df = load_full(file_bytes, file_name)[list(selected_cols)]
    else:
        df = load_preview(file_bytes, file_name, nrows=num_rows)[list(selected_cols)]
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_out = csv_buffer.getvalue().encode("utf-8")
    json_out = df.to_json(orient="records", indent=2).encode("utf-8")
    return csv_out, json_out, len(df)

st.set_page_config(page_title="IngestReady", page_icon="🚀", layout="wide")

st.markdown("""
<style>
/* Prevent full-page fade during reruns */
.stApp { opacity: 1 !important; transition: none !important; }
[data-testid="stAppViewContainer"] { opacity: 1 !important; transition: none !important; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 IngestReady")
st.markdown("Trim, clean, and prepare your CSV files for ingestion into Data360.")

st.info(
    "**Working with a file larger than 200 MB?** "
    "This web app may be slow or crash with very large files. "
    "For big files, download IngestReady and run it on your own machine — no file size limits.  \n"
    "👉 [Download the desktop version](https://github.com/sgattoju9/cvs-clean-up/archive/refs/heads/main.zip)"
)

# ── Step 1: Upload ──────────────────────────────────────────────────────────
st.header("Step 1: Upload Your CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.success(f"File uploaded: **{uploaded_file.name}** ({file_size_mb:.1f} MB)")

    if file_size_mb > 200:
        st.warning(
            f"This file is **{file_size_mb:.0f} MB** — too large for the cloud version. "
            "Run this app locally on your machine for best performance."
        )

    file_bytes = uploaded_file.read()

    # ── Step 2: Row options ─────────────────────────────────────────────────
    st.header("Step 2: How Many Rows Do You Want to Keep?")

    total_rows = count_rows(file_bytes)
    st.success(f"This file contains **{total_rows:,} total rows**.")

    keep_all = st.checkbox(
        f"Use full dataset ({total_rows:,} rows) for download",
        value=False,
        key="keep_all"
    )

    col1, _ = st.columns([1, 3])
    with col1:
        num_rows = st.number_input(
            "Number of rows to keep",
            min_value=1,
            max_value=total_rows,
            value=min(1000, total_rows),
            step=100,
            disabled=keep_all
        )

    if keep_all:
        st.info(f"Download will include **all {total_rows:,} rows**.")
    else:
        st.info(f"Download will include **{num_rows:,} of {total_rows:,} rows**.")

    # ── Step 3: Select columns ───────────────────────────────────────────────
    st.header("Step 3: Select Columns to Keep")
    st.markdown("Check the columns you want in your final file. Uncheck anything you don't need.")

    preview_df = load_preview(file_bytes, uploaded_file.name)
    all_columns = list(preview_df.columns)

    col_a, col_b, _ = st.columns([1, 1, 4])
    with col_a:
        select_all = st.button("✅ Select All")
    with col_b:
        deselect_all = st.button("❌ Deselect All")

    if select_all:
        for col_name in all_columns:
            st.session_state[f"chk_{col_name}"] = True
    if deselect_all:
        for col_name in all_columns:
            st.session_state[f"chk_{col_name}"] = False

    for col_name in all_columns:
        if f"chk_{col_name}" not in st.session_state:
            st.session_state[f"chk_{col_name}"] = True

    num_cols_per_row = 4
    col_rows = [all_columns[i:i+num_cols_per_row] for i in range(0, len(all_columns), num_cols_per_row)]

    selected = []
    for row in col_rows:
        cols = st.columns(num_cols_per_row)
        for i, col_name in enumerate(row):
            if cols[i].checkbox(col_name, key=f"chk_{col_name}"):
                selected.append(col_name)

    st.markdown(f"**{len(selected)} of {len(all_columns)} columns selected**")

    # ── Step 4: Preview & Download ───────────────────────────────────────────
    st.header("Step 4: Preview & Download")

    if len(selected) == 0:
        st.warning("Please select at least one column above.")
    else:
        base_name = os.path.splitext(uploaded_file.name)[0]

        st.subheader("Preview (first 10 rows)")
        st.dataframe(preview_df[selected].head(10), use_container_width=True)

        # ── Downloads ────────────────────────────────────────────────────────
        st.subheader("Choose your download format:")

        csv_bytes_out, json_bytes_out, row_count = make_download_bytes(
            file_bytes, uploaded_file.name, tuple(selected), keep_all, num_rows
        )

        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="⬇️ Download as CSV",
                data=csv_bytes_out,
                file_name=f"{base_name}_cleaned.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                label="⬇️ Download as JSON",
                data=json_bytes_out,
                file_name=f"{base_name}_cleaned.json",
                mime="application/json",
                use_container_width=True
            )

        size_kb = len(csv_bytes_out) / 1024
        if size_kb > 1024:
            st.info(f"Output size: **{size_kb/1024:.2f} MB** ({row_count:,} rows)")
        else:
            st.info(f"Output size: **{size_kb:.1f} KB** ({row_count:,} rows)")

else:
    st.info("👆 Upload a CSV file above to get started.")

    with st.expander("How does this work?"):
        st.markdown("""
        1. **Upload** your CSV file
        2. **Choose rows** — enter how many rows to keep, or check the box to use all rows
        3. **Choose columns** — check/uncheck the columns you want
        4. **Download** as CSV or JSON

        > **Large files (200MB+):** Run this app locally on your machine for best performance.
        """)

    with st.expander("💻 How to run this app on your own computer (step-by-step)"):
        st.markdown("""
        You can run this tool on your own machine — no internet needed, no file size limits.

        ---

        ### Step 1 — Check if Python is installed
        Open a **Terminal** (Mac) or **Command Prompt** (Windows) and type:
        ```
        python3 --version
        ```
        If you see `Python 3.x.x`, skip to Step 3.

        ---

        ### Step 2 — Install Python (only if needed)
        - Go to **https://www.python.org/downloads/**
        - Download and run the installer
        - **Windows only:** check **"Add Python to PATH"** before clicking Install

        ---

        ### Step 3 — Download this app
        - [Download ZIP](https://github.com/sgattoju9/cvs-clean-up/archive/refs/heads/main.zip)
        - Unzip the folder to your Desktop

        ---

        ### Step 4 — Install packages and run
        In Terminal / Command Prompt, navigate to the unzipped folder, then run:
        ```
        pip install -r requirements.txt
        streamlit run app.py
        ```
        Your browser will open automatically at **http://localhost:8501**
        """)
