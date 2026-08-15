# Stream Forge - R6 Only

This project contains only the coding work for **R6: React Flow Dashboard Developer** in Project 2 - Stream Forge.

## Included work
- Week 1: Scaffold React app with React Flow, build topology canvas skeleton, create placeholder DAG nodes, connect to mock API, style baseline theme
- Week 2: Build DAG visualization bound to live topology, add node status indicators, connect FastAPI metrics endpoint stub, polish DAG edges and animations, improve usability
- Mid-Project Review: Build live audit visualization panel, wire real-time throughput numbers, add per-partition breakdown view, add windowing-correctness widget
- Week 3 : Telemetry & Recovery Visualization: Implemented a telemetry dashboard displaying per-stream metrics and worker health, added live partition-rebalancing visualization and worker crash/recovery animation driven by real metrics feeds, and polished the telemetry UI for chaos-testing demonstration.
- Week 4 :  Connect Prometheus metrics to React Flow dashboard, Add bottleneck node highlighting ,Final UI polish ,Cross-browser testing, Final demo walkthroug

Add live partition-rebalancing visualization

## Run backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

## Run frontend
cd frontend
npm install
npm run dev
