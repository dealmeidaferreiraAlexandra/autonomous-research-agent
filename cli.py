from src.agent import build_report


def main():
    topic = input("Topic to research: ").strip()
    if not topic:
        print("No topic provided.")
        return

    report = build_report(topic)

    print("\n=== MODE ===")
    print(report.mode)

    print("\n=== EXECUTIVE SUMMARY ===")
    print(report.executive_summary)

    print("\n=== KEY INSIGHTS ===")
    for item in report.key_insights:
        print(f"- {item}")

    print("\n=== RECOMMENDATIONS ===")
    for item in report.recommendations:
        print(f"- {item}")

    print("\n=== REFERENCES ===")
    for ref in report.references:
        print(f"- [{ref.source_type}] {ref.title} — {ref.url_or_path}")


if __name__ == "__main__":
    main()