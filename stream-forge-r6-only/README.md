# Stream Forge - R6 Only

This project contains only the coding work for **R6: React Flow Dashboard Developer** in Project 2 - Stream Forge.

## Included work
- Week 1: Scaffold React app with React Flow, build topology canvas skeleton, create placeholder DAG nodes, connect to mock API, style baseline theme
- Week 2: Build DAG visualization bound to live topology, add node status indicators, connect FastAPI metrics endpoint stub, polish DAG edges and animations, improve usability
- Mid-Project Review: Build live audit visualization panel, wire real-time throughput numbers, add per-partition breakdown view, add windowing-correctness widget
- Week 3

## Run backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

## Run frontend
cd frontend
npm install
npm run dev
