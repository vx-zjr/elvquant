from qts.simple import run_synthetic_demo


def main() -> None:
    report = run_synthetic_demo()
    print(report.text)


if __name__ == "__main__":
    main()
