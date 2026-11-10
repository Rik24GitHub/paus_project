# Group 7 Store Sales Explorer

A Streamlit app for exploring the supplied store sales dataset and reviewing the regression results included with the project.

## Project files

```text
.
├── .streamlit/
│   └── config.toml
├── .gitignore
├── GROUP_7_raw_data.csv
├── README.md
├── requirements.txt
└── streamlit_app.py
```

The CSV is bundled with the app, so no separate data upload or database setup is needed. The optional CSV upload in the sidebar can be used to explore another file with the same expected columns.

## Run on your computer

Use Python 3.10 or newer. From this folder, install the packages and start the app:

```bash
python -m venv .venv
```

Activate the environment, then run:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Upload to GitHub and deploy

1. Create a GitHub repository and upload the files and folders in this project. Keep `streamlit_app.py`, `requirements.txt`, and `GROUP_7_raw_data.csv` at the repository root; keep `config.toml` inside `.streamlit/`.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Choose **Create app**, select your repository and branch, and set the app file to `streamlit_app.py`.
4. Select **Deploy**. Streamlit installs the packages listed in `requirements.txt`.

The included data file is about 32.6 MB and is within GitHub's regular per-file limit. If the data changes frequently or grows substantially, consider Git LFS or a hosted data source.

## What the app shows

- Sales totals, average sales per row, and sales trends
- Filters for date, city, product family, and store number
- Breakdowns by product family, store type, and promotion flag
- A preview and CSV download for the filtered rows
- A summary of the supplied cross-validation and model-comparison findings

The supplied reports give different validation ASE values. The app displays them as separate reported results and does not claim to reproduce or refit the original SAS model-selection procedures.

## Data visibility

The bundled CSV will be visible to anyone who can access the GitHub repository. Use a private repository or remove the data before upload if the file should not be publicly accessible. Streamlit Community Cloud can deploy from a private repository when connected with the required GitHub access.
