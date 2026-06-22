import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(
    page_title="CSV Cleanup Tool",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 CSV Cleanup Tool")
st.markdown("Upload a large CSV, trim rows, pick columns, and download a clean file.")

# ── Step 1: Upload ──────────────────────────────────────────────────────────
st.header("Step 1: Upload Your CSV File")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.success(f"File uploaded: **{uploaded_file.name}** ({file_size_mb:.1f} MB)")

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

    # Read only the rows we need — fast even for 2GB files
    with st.spinner("Reading file headers and first rows (this is fast even for large files)..."):
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

    # Show a "select all / deselect all" toggle
    col_a, col_b, _ = st.columns([1, 1, 4])
    with col_a:
        select_all = st.button("✅ Select All")
    with col_b:
        deselect_all = st.button("❌ Deselect All")

    # Manage selection state
    if "selected_columns" not in st.session_state:
        st.session_state.selected_columns = all_columns.copy()

    if select_all:
        for col_name in all_columns:
            st.session_state[f"chk_{col_name}"] = True
    if deselect_all:
        for col_name in all_columns:
            st.session_state[f"chk_{col_name}"] = False

    # Display columns in a 4-column grid with checkboxes
    num_cols_per_row = 4
    rows = [all_columns[i:i+num_cols_per_row] for i in range(0, len(all_columns), num_cols_per_row)]

    selected = []
    for row in rows:
        cols = st.columns(num_cols_per_row)
        for i, col_name in enumerate(row):
            default = col_name in st.session_state.selected_columns
            if cols[i].checkbox(col_name, value=default, key=f"chk_{col_name}"):
                selected.append(col_name)

    st.session_state.selected_columns = selected

    st.markdown(f"**{len(selected)} of {len(all_columns)} columns selected**")

    # ── Step 4: Preview & Download ───────────────────────────────────────────
    st.header("Step 4: Preview & Download")

    if len(selected) == 0:
        st.warning("Please select at least one column above.")
    else:
        clean_df = df[selected]

        st.subheader("Preview (first 10 rows)")
        st.dataframe(clean_df.head(10), use_container_width=True)

        # Convert to CSV in memory
        csv_buffer = io.StringIO()
        clean_df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        output_filename = os.path.splitext(uploaded_file.name)[0] + "_cleaned.csv"

        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_bytes,
            file_name=output_filename,
            mime="text/csv",
            use_container_width=True
        )

        size_kb = len(csv_bytes) / 1024
        if size_kb > 1024:
            st.info(f"Output file size: **{size_kb/1024:.2f} MB** — easily openable in Excel or Google Sheets.")
        else:
            st.info(f"Output file size: **{size_kb:.1f} KB** — easily openable in Excel or Google Sheets.")

else:
    st.info("👆 Upload a CSV file above to get started.")

    with st.expander("How does this work?"):
        st.markdown("""
        1. **Upload** your CSV file (even 2GB+ files work)
        2. **Choose rows** — enter how many rows to keep (e.g. 1000)
        3. **Choose columns** — check/uncheck the columns you want
        4. **Download** the clean, trimmed CSV — opens easily in Excel or Google Sheets

        > This tool only reads the rows you ask for, so it handles huge files quickly without loading everything into memory.
        """)
