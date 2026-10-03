.PHONY: load ratios screener peers nlp cluster valuation report test dashboard api verify clean

load:
    python -m src.etl.run_etl

ratios:
    python -m src.analytics.build_ratios

screener:
    python scripts/run_screener.py

peers:
    python scripts/run_peers.py

nlp:
    python scripts/run_nlp.py

cluster:
    python scripts/run_clustering.py

valuation:
    python scripts/run_valuation.py

report:
    python -m src.reports.generate_reports

test:
    pytest tests/ -v

dashboard:
    streamlit run src/dashboard/app.py

api:
    uvicorn src.api.main:app --host 127.0.0.1 --port 8000

verify:
    python scripts/verify_pipeline.py

clean:
    python scripts/clean_generated.py
