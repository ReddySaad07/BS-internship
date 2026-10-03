import subprocess
import sys


STEPS = [
    [
        sys.executable,
        "-m",
        "src.etl.run_etl",
    ],
    [
        sys.executable,
        "-m",
        "src.analytics.build_ratios",
    ],
    [
        sys.executable,
        "scripts/run_screener.py",
    ],
    [
        sys.executable,
        "scripts/run_peers.py",
    ],
    [
        sys.executable,
        "scripts/run_nlp.py",
    ],
    [
        sys.executable,
        "scripts/run_clustering.py",
    ],
    [
        sys.executable,
        "scripts/run_valuation.py",
    ],
    [
        sys.executable,
        "scripts/run_portfolio.py",
    ],
    [
        sys.executable,
        "-m",
        "src.reports.generate_reports",
    ],
]


def main():
    for number, command in enumerate(
        STEPS,
        start=1,
    ):
        print()
        print("=" * 70)
        print(
            f"STEP {number}/{len(STEPS)}"
        )
        print(
            " ".join(command)
        )
        print("=" * 70)

        result = subprocess.run(
            command
        )

        if result.returncode != 0:
            print()
            print(
                f"Pipeline stopped at step {number}."
            )
            sys.exit(
                result.returncode
            )

    print()
    print("=" * 70)
    print("MASTER PIPELINE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
