# Git & GitHub Assignment

## Recommended repository structure
```text
Data-Analyst-Internship-FinTech-2-Week-Prerequisite/
├── 01_Week1_Excel/
├── 02_Week1_SQL/
├── 03_Week1_Python/
├── 04_Week1_EDA/
├── 05_Week1_PowerBI/
├── 06_Week1_Statistics/
├── 07_Week2_Stock_Market/
├── 08_Week2_API_JSON/
├── 09_Week2_Git_GitHub/
├── 10_Week2_Software_Development/
├── 11_Week2_FinTech/
└── README.md
```

## First-time setup
```bash
git init
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git add .
git commit -m "Add two-week data analyst internship prerequisite"
git push -u origin main
```

## Normal workflow
```bash
git status
git add .
git commit -m "Update analytics assignments"
git push
```

## Branch example
```bash
git checkout -b feature/sql-analysis
# make changes
git add .
git commit -m "Add SQL analysis queries"
git push -u origin feature/sql-analysis
```

## Pull request
Open the branch on GitHub and create a Pull Request into `main`.

## Important
Do not commit passwords, API keys, access tokens, or private credentials. Use environment variables or local configuration files for secrets.
