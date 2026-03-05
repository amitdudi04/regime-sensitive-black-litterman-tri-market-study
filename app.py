from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio_optimization.models.black_litterman import BlackLittermanOptimizer

try:
    from empirical_study import TICKER_NAME_MAP
except ImportError:
    TICKER_NAME_MAP = {}

app = FastAPI(title="Black-Litterman Portfolio Intelligence UI")

# Mount frontend static directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/results", StaticFiles(directory="results"), name="results")

class OptimizationRequest(BaseModel):
    tickers: List[str]
    start_date: str
    end_date: str
    views: Dict[str, float]
    confidence: Dict[str, float]

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/about")
async def read_about():
    return FileResponse('frontend/about.html')

@app.get("/empirical")
async def read_empirical():
    return FileResponse('frontend/empirical.html')

@app.post("/api/empirical_study")
async def trigger_empirical_study():
    try:
        import subprocess
        import os
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        # Run the empirical study engine
        # Since it generates local CSVs and PNGs inside /results natively, we just await completion
        result = subprocess.run(
            [sys.executable, 'empirical_study.py'], 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace',
            env=env
        )
        if result.returncode != 0:
            raise Exception(f"Study failed with code {result.returncode}:\n{result.stderr}")
            
        return {"status": "success", "message": "Tri-Market Analytical Pipeline Executed."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/asset_dictionary")
async def get_asset_dictionary():
    """Return the global translation map pairing raw tickers to English company names."""
    return {"status": "success", "data": TICKER_NAME_MAP}

@app.post("/api/optimize")
async def optimize_portfolio(req: OptimizationRequest):
    try:
        # 1. Initialize mathematical optimizer
        optimizer = BlackLittermanOptimizer(
            req.tickers, 
            req.start_date, 
            req.end_date,
            name_mapping=TICKER_NAME_MAP
        )
        
        # 2. Run both models and extract arrays
        # (Compare models automatically outputs Markowitz and Equal Weights for benchmarking alongside the BL results)
        results = optimizer.compare_models(req.views, req.confidence)
        
        # 3. Clean up generic numpy structures so FastAPI can serialize to JSON for the web frontend
        def numpy_to_native(d: dict) -> dict:
            clean = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    clean[k] = numpy_to_native(v)
                elif hasattr(v, 'tolist'):
                    clean[k] = v.tolist()
                elif hasattr(v, 'item'):
                    clean[k] = v.item()
                else:
                    clean[k] = v
            return clean

        payload = numpy_to_native(results)
        payload["mapped_tickers"] = optimizer.ticker_list

        return {"status": "success", "data": payload}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    print("🚀 Running Black-Litterman Portfolio Web Intelligence Engine")
    print("🌍 Navigate to: http://localhost:8000")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
