# Stream Forge — R5 Only

This directory contains **only R5: Observability & Reliability Engineer**'s
work for Project 2 (Stream Forge), all 4 weeks + Mid-Project Review. It does
not modify R2's or R6's code — it's a standalone package that reads Kafka
metadata and exposes Prometheus metrics for the rest of the team to consume.

## Deliverable → file map

| Week | Day | Deliverable | File |
|---|---|---|---|
| 1 | Mon | Prometheus + Grafana locally | `monitoring/docker-compose.monitoring.yml`, `monitoring/prometheus.yml` |
| 1 | Tue | Metrics taxonomy | `src/stream_forge_r5/metrics.py`, `docs/metrics_taxonomy.md` |
| 1 | Wed | Instrument producer | `src/stream_forge_r5/producer_instrumentation.py` |
| 1 | Thu | Broker health-check scripts | `src/stream_forge_r5/broker_health.py` |
| 1 | Fri | Chaos-testing plan | `docs/chaos_testing_plan.md` |
| 2 | Mon–Tue | Worker counters + lag metric | `src/stream_forge_r5/consumer_instrumentation.py` |
| 2 | Wed | Grafana dashboard panels | `monitoring/grafana/stream-forge-dashboard.json` |
| 2 | Thu | Baseline throughput benchmark | `throughput_audit.benchmark_baseline` |
| 2 | Fri | Report tooling prep | `scripts/generate_reports.py` |
| Mid-Review | Mon–Wed | Execute/capture/aggregate audit | `throughput_audit.run_throughput_audit` |
| Mid-Review | Thu | Identify bottlenecks | `src/stream_forge_r5/bottleneck_analysis.py` |
| Mid-Review | Fri | Audit report | `docs/mid_project_audit_report.md` |
| 3 | Mon–Thu | Design/verify/automate chaos test | `src/stream_forge_r5/chaos/chaos_test.py` |
| 3 | Fri | Chaos results doc | `docs/chaos_testing_results.md` |
| 4 | Mon | Client metrics on all workers | reuses `metrics.py` + `consumer_instrumentation.py` (nothing new to add — the taxonomy already covers every worker) |
| 4 | Tue | Connect metrics to dashboard | `src/stream_forge_r5/api.py` (`/metrics` — R6 points its stub at this) |
| 4 | Wed | Validate metric accuracy | `tests/` (every metric has an assertion against it) |
| 4 | Thu | Alerting rules | `src/stream_forge_r5/alerting.py`, `monitoring/alerts.yml` |
| 4 | Fri | Final report | `docs/final_observability_report.md` |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
make install
cp .env.example .env
make test
```

```bash
make monitoring-up   # Prometheus on :9090, Grafana on :3000 (admin/admin)
make api             # FastAPI /metrics on :9200
make alerts          # regenerate monitoring/alerts.yml from .env thresholds
make reports          # regenerate the three Markdown reports
```

## Design decisions (so I can answer "why this and not X")

**One `metrics.py` file, not metrics scattered per-module.**
Every Prometheus metric is declared exactly once, with one name and one
label set. If producer code and consumer code each declared their own
`events_total` counter, you'd get two metrics with overlapping meaning and
no single source of truth for what a dashboard panel is actually querying.

**A private `CollectorRegistry()` instead of Prometheus's global default registry.**
The default registry is a module-level global — importing `metrics.py`
twice (which pytest does across test files) would raise "duplicated
metric" errors. A local registry sidesteps that and also means the FastAPI
`/metrics` endpoint only ever exposes *this service's* metrics, not
whatever else happens to be registered process-wide.

**Composition over inheritance for `InstrumentedProducer`.**
`confluent_kafka.Producer` is a C-extension class — subclassing it doesn't
give you a clean hook to wrap `produce()`, and it would drag the whole
Kafka client into every instrumentation unit test. Wrapping it behind a
small `SupportsProduce` Protocol means tests use a five-line fake instead
of a running Kafka broker.

**`Protocol` classes instead of importing `confluent_kafka` types directly
into `chaos.py`, `throughput_audit.py`, `consumer_instrumentation.py`.**
Each of these only needs one or two methods off a Kafka object
(`get_watermark_offsets`, `committed`, or nothing at all for chaos). Typing
against a `Protocol` — structural typing — means any object with that
shape works, so tests never need a real Kafka cluster and the modules stay
decoupled from *which* Kafka client R1 ends up using.

**Frozen `dataclasses` for compute results (`PartitionSample`, `AuditResult`,
`ChaosResult`, `Bottleneck`, `BrokerHealth`), Pydantic only in `config.py`.**
Pydantic's job is validating *untrusted input* — env vars, JSON payloads.
These dataclasses hold values this codebase already computed and trusts;
adding validation there is overhead with no payoff. `frozen=True` also
buys immutability for free, appropriate for "here's what the audit found",
which shouldn't be mutated after the fact.

**One `render_report()` instead of four near-identical report functions.**
Every Friday report is "a title plus some Markdown sections" — only the
sections differ. Building each report string by hand four times would mean
four places to fix a Markdown formatting bug instead of one.

**Why chaos testing sends `SIGKILL`, not `SIGTERM`.**
The use case is "Worker Node #4 crashes" — an ungraceful failure. `SIGTERM`
would test graceful shutdown, a different (and easier) scenario R4 already
covers with normal deploys. `SIGKILL` is the only way to actually simulate
a crash the way the requirement describes it.

**Why the audit and lag sampling don't hold a lock or use `asyncio`.**
Reading Kafka watermark offsets over a fixed window (`sleep()` + diff) is
inherently sequential and I/O bound in a way `asyncio` wouldn't meaningfully
speed up — the bottleneck is waiting for the sample window to elapse, not
CPU or blocked concurrent calls. Introducing async here would add
complexity (event loop, awaitable Kafka client) without a real throughput
gain.

**Why `find_bottleneck_partitions` uses a relative deviation threshold
(default 20%) instead of an absolute events/sec cutoff.**
An absolute cutoff (e.g. "below 20,000 events/sec") breaks the moment the
target throughput changes. A relative threshold — "more than 20% below the
group's own average" — stays correct regardless of what the target is,
and is what actually indicates an *imbalance* rather than just low volume.

## What I deliberately left out

- No custom metrics-export protocol — `prometheus-client`'s
  `generate_latest()` already produces the exact text format Prometheus
  scrapes, so writing one would just be reinventing that.
- No bespoke YAML dumper for `alerts.yml` — `build_alert_rules()` returns
  plain `dict`/`list`, and `yaml.safe_dump` already turns that into valid
  Prometheus rule syntax.
- No retry/backoff logic in `broker_health.py` — a health check that
  silently retries before reporting unhealthy would hide the exact
  intermittent failures it exists to catch. One probe, one honest result.
