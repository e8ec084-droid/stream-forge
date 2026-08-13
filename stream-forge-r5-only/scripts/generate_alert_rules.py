"""CLI entry point: regenerates monitoring/alerts.yml from ObservabilitySettings."""

from pathlib import Path

from stream_forge_r5.alerting import write_alert_rules
from stream_forge_r5.config import get_observability_settings

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "monitoring" / "alerts.yml"


def main() -> None:
    write_alert_rules(get_observability_settings(), OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
