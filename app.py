import streamlit as st
import pandas as pd
import io
import re
import requests

st.set_page_config(
    page_title="CSV Cleanup Tool",
    page_icon="🧹",
    layout="wide"
)

st.title("🧹 CSV Cleanup Tool")
st.markdown("Paste a Google Drive link to your CSV, trim rows, pick columns, and download a clean file.")


def get_drive_file_id(url):
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_drive_response(file_id):
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    session = requests.Session()
    response = session.get(download_url, stream=True)
    token = None
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break
    if token:
        response = session.get(download_url, params={'confirm': token}, stream=True)
    return response


def load_csv_from_drive(file_id, nrows):
    response = get_drive_response(file_id)
    try:
        df = pd.read_csv(response.raw, nrows=nrows, low_memory=False)
    except UnicodeDecodeError:
        response = get_drive_response(file_id)
        df = pd.read_csv(response.raw, nrows=nrows, low_memory=False, encoding='latin-1')
    return df


# ── Step 1: Google Drive Link ────────────────────────────────────────────────
st.header("Step 1: Paste Your Google Drive Link")
st.markdown("> Make sure your file is set to **Anyone with the link can view** in Google Drive.")

drive_url = st.text_input("Google Drive file link", placeholder="https://drive.google.com/file/d/...")

if drive_url:
    file_id = get_drive_file_id(drive_url)
    if not file_id:
        st.error("Could not read that link. Make sure it's a valid Google Drive file link.")
    else:

        # ── Step 2: Choose how many rows ────────────────────────────────────
        st.header("Step 2: How Many Rows Do You Want to Keep?")
        col1, col2 = st.columns([1, 2])
        with col1:
            num_rows = st.number_input(
                "Number of rows to keep",
                min_value=1,
                max_value=1_000_000,
                value=1000,
                step=100,
                help="Enter how many rows you want in your output file."
            )
        st.info(f"The output file will contain up to **{num_rows:,} rows**.")

        with st.spinner("Downloading file from Google Drive..."):
            try:
                df = load_csv_from_drive(file_id, num_rows)
                st.success(f"Loaded **{len(df):,} rows** and **{len(df.columns):,} columns** from your file.")
            except Exception as e:
                st.error(f"Could not load the file. Make sure the link is public and points to a CSV file.\n\nError: {e}")
                st.stop()

        # ── Step 3: Choose columns ───────────────────────────────────────────
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

        # ── Step 4: Preview & Download ───────────────────────────────────────
        st.header("Step 4: Preview & Download")

        if len(selected) == 0:
            st.warning("Please select at least one column above.")
        else:
            clean_df = df[selected]

            st.subheader("Preview (first 10 rows)")
            st.dataframe(clean_df.head(10), use_container_width=True)

            st.subheader("Choose your download format:")
            dl_col1, dl_col2, dl_col3 = st.columns(3)

            csv_buffer = io.StringIO()
            clean_df.to_csv(csv_buffer, index=False)
            csv_bytes = csv_buffer.getvalue().encode("utf-8")

            json_bytes = clean_df.to_json(orient="records", indent=2).encode("utf-8")
            xml_bytes = clean_df.to_xml(index=False).encode("utf-8")

            with dl_col1:
                st.download_button(
                    label="⬇️ Download as CSV",
                    data=csv_bytes,
                    file_name="cleaned_file.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with dl_col2:
                st.download_button(
                    label="⬇️ Download as JSON",
                    data=json_bytes,
                    file_name="cleaned_file.json",
                    mime="application/json",
                    use_container_width=True
                )
            with dl_col3:
                st.download_button(
                    label="⬇️ Download as XML",
                    data=xml_bytes,
                    file_name="cleaned_file.xml",
                    mime="application/xml",
                    use_container_width=True
                )

else:
    st.info("👆 Paste a Google Drive link above to get started.")
    with st.expander("How does this work?"):
        st.markdown("""
        1. **Upload your CSV to Google Drive** and set sharing to "Anyone with the link can view"
        2. **Paste the link** into the box above
        3. **Choose rows** — enter how many rows to keep
        4. **Choose columns** — check/uncheck the columns you want
        5. **Download** as CSV, JSON, or XML
        """)
