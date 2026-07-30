# 🧹 CSV Cleanup Tool

A simple web app to upload a CSV file, trim rows, pick columns, search your data, and download a clean file.

**Online version:** [Open in browser](https://cvs-clean-up.streamlit.app)

> If your file is larger than 200 MB, the online version may be slow or crash.
> Follow the steps below to run the app on your own computer — no file size limits.

---

## 💻 Run on Your Own Computer (Step-by-Step)

### Step 1 — Download the app

Click the green **Code** button on this page, then click **Download ZIP**.
Unzip the folder somewhere on your computer (e.g. your Desktop).

---

### Step 2 — Check if Python is installed

Open a **Terminal** (Mac) or **Command Prompt** (Windows) and type:

```
python3 --version
```

If you see something like `Python 3.10.x`, skip to Step 4.
If you get an error, continue to Step 3.

---

### Step 3 — Install Python (only if needed)

1. Go to **https://www.python.org/downloads/**
2. Click the big yellow **Download Python** button
3. Run the installer — on Windows, check **"Add Python to PATH"** before clicking Install
4. Once done, close and reopen your Terminal / Command Prompt, then re-run Step 2

---

### Step 4 — Open the app folder in Terminal

**Mac:**
1. Open **Terminal** (search for it in Spotlight)
2. Type `cd ` (with a space after), then drag the unzipped folder into the Terminal window and press Enter

**Windows:**
1. Open the unzipped folder in File Explorer
2. Click the address bar at the top, type `cmd`, and press Enter

---

### Step 5 — Set up the environment (one time only)

Copy and paste these commands one at a time, pressing Enter after each:

```
python3 -m venv venv
```

**Mac:**
```
source venv/bin/activate
```

**Windows:**
```
venv\Scripts\activate
```

Then install the required packages:
```
pip install -r requirements.txt
```

---

### Step 6 — Start the app

```
python3 -m streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501**

---

### Step 7 — Next time you want to use it

You only need to do Steps 4 and 6 each time. Steps 5 is one-time setup only.

---

## What the app does

1. **Upload** a CSV file from your computer
2. **Choose rows** — enter how many rows to keep in the output
3. **Choose columns** — check/uncheck the columns you want
4. **Search** — optionally type a keyword to filter rows
5. **Download** the cleaned file as CSV or JSON

---

## Need help?

If something goes wrong, check that:
- Python 3.8 or higher is installed (`python3 --version`)
- You activated the virtual environment before running (Step 5)
- You are in the correct folder in Terminal
