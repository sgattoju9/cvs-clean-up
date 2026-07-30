import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(
    page_title="IngestReady",
    page_icon="🚀",
    layout="wide"
)

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
            "If you experience slowness or crashes, run this app locally on your machine instead. "
            "Ask your admin for setup instructions."
        )

    # ── Step 2: Choose how many rows ────────────────────────────────────────
    st.header("Step 2: How Many Rows Do You Want to Keep?")

    col1, col2 = st.columns([1, 2])
    with col1:
        num_rows = st.number_input(
            "Number of rows to keep",
            min_value=1,
            max_value=1_000_000,
            value=1000,
            step=100,
            help="Enter how many rows you want in your output file. For a quick preview, 500–1000 is ideal."
        )

    st.info(f"The output file will contain up to **{num_rows:,} rows**.")

    with st.spinner("Reading file..."):
        try:
            df = pd.read_csv(uploaded_file, nrows=num_rows, low_memory=False, encoding="utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, nrows=num_rows, low_memory=False, encoding="latin-1")

    st.success(f"Loaded **{len(df):,} rows** and **{len(df.columns):,} columns** from your file.")

    # ── Step 3: Choose columns ───────────────────────────────────────────────
    st.header("Step 3: Select Columns to Keep")
    st.markdown("Check the columns you want in your final file. Uncheck anything you don't need.")

    all_columns = list(df.columns)

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
    rows = [all_columns[i:i+num_cols_per_row] for i in range(0, len(all_columns), num_cols_per_row)]

    selected = []
    for row in rows:
        cols = st.columns(num_cols_per_row)
        for i, col_name in enumerate(row):
            if cols[i].checkbox(col_name, key=f"chk_{col_name}"):
                selected.append(col_name)

    st.session_state.selected_columns = selected
    st.markdown(f"**{len(selected)} of {len(all_columns)} columns selected**")

    # ── Step 4: Preview & Download ───────────────────────────────────────────
    st.header("Step 4: Preview & Download")

    if len(selected) == 0:
        st.warning("Please select at least one column above.")
    else:
        clean_df = df[selected]
        base_name = os.path.splitext(uploaded_file.name)[0]

        # ── Keyword Filter ──────────────────────────────────────────────────
        st.subheader("🔍 Search Your Data (Optional)")
        st.markdown("Type any word or value to show only rows that contain it. Leave it blank to see all rows.")

        search_term = st.text_input(
            "Search across all columns:",
            placeholder="e.g. Texas  or  active  or  john@email.com",
            key="search_filter"
        )

        display_df = clean_df

        if search_term.strip():
            mask = clean_df.apply(
                lambda col: col.astype(str).str.contains(search_term.strip(), case=False, na=False)
            ).any(axis=1)
            filtered = clean_df[mask]
            if len(filtered) == 0:
                st.warning("No rows matched that search. Showing all rows instead.")
            else:
                display_df = filtered
                st.success(f"Found **{len(filtered):,} rows** containing **\"{search_term}\"**.")

        # ── Preview ─────────────────────────────────────────────────────────
        st.subheader("Preview (first 10 rows)")
        st.dataframe(display_df.head(10), use_container_width=True)

        # ── Downloads ────────────────────────────────────────────────────────
        st.subheader("Choose your download format:")
        dl_col1, dl_col2 = st.columns(2)

        csv_buffer = io.StringIO()
        display_df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")
        json_bytes = display_df.to_json(orient="records", indent=2).encode("utf-8")

        with dl_col1:
            st.download_button(
                label="⬇️ Download as CSV",
                data=csv_bytes,
                file_name=f"{base_name}_cleaned.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                label="⬇️ Download as JSON",
                data=json_bytes,
                file_name=f"{base_name}_cleaned.json",
                mime="application/json",
                use_container_width=True
            )

        size_kb = len(csv_bytes) / 1024
        if size_kb > 1024:
            st.info(f"Output size: **{size_kb/1024:.2f} MB** ({len(display_df):,} rows)")
        else:
            st.info(f"Output size: **{size_kb:.1f} KB** ({len(display_df):,} rows)")

else:
    st.info("👆 Upload a CSV file above to get started.")

    with st.expander("How does this work?"):
        st.markdown("""
        1. **Upload** your CSV file
        2. **Choose rows** — enter how many rows to keep
        3. **Choose columns** — check/uncheck the columns you want
        4. **Filter** — optionally type a keyword to narrow down rows
        5. **Download** as CSV or JSON

        > **Large files (200MB+):** Run this app locally on your machine for best performance.
        > See the setup guide below.
        """)

    with st.expander("💻 How to run this app on your own computer (step-by-step)"):
        st.markdown("""
        You can run this tool on your own machine — no internet needed, no file size limits.
        Follow these steps:

        ---

        ### Step 1 — Check if Python is installed
        Open a **Terminal** (Mac/Linux) or **Command Prompt** (Windows) and type:
        ```
        python --version
        ```
        If you see something like `Python 3.10.x`, you're good. If you get an error, continue to Step 2.

        ---

        ### Step 2 — Install Python (only if needed)
        - Go to **https://www.python.org/downloads/**
        - Download the latest version for your operating system
        - Run the installer. **On Windows**, check the box that says **"Add Python to PATH"** before clicking Install

        ---

        ### Step 3 — Download this app
        - Click this link to download: [Download ZIP](https://github.com/sgattoju9/cvs-clean-up/archive/refs/heads/main.zip)
        - Unzip the downloaded file to a folder on your computer (e.g. your Desktop)

        ---

        ### Step 4 — Install the required packages
        In your Terminal / Command Prompt, navigate to the folder where you unzipped the app:
        ```
        cd path/to/csv-cleanup-tool
        ```
        Then run:
        ```
        pip install -r requirements.txt
        ```
        This installs Streamlit and pandas — the only two packages needed.

        ---

        ### Step 5 — Run the app
        ```
        streamlit run app.py
        ```
        Your browser will open automatically at **http://localhost:8501**

        ---

        **Having trouble?** Common fixes:
        - If `pip` is not found, try `pip3` instead
        - If `streamlit` is not found after installing, close and reopen your Terminal
        - On Windows, run Command Prompt **as Administrator** if you get permission errors
        """)
