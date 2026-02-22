from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["POST"], # Specifically allows POST as requested
    allow_headers=["*"], # Allows all headers
)

# Load the data from your telemetry bundle
# Ensure this matches the JSON you downloaded
with open('q-vercel-latency.json', 'r') as f:
    TELEMETRY_DATA = json.load(f)

@app.post("/api/metrics")
async def get_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    
    results = {}
    for region in regions:
        # Filter records for the requested region
        region_recs = [d for d in TELEMETRY_DATA if d["region"] == region]
        if not region_recs:
            continue

        latencies = [d["latency_ms"] for d in region_recs]
        uptimes = [d["uptime_pct"] for d in region_recs]
        
        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for l in latencies if l > threshold)
        }
    
    return results
