from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional
import uuid
from agent.planner import create_research_plan
from agent.validator import validate_plan
from agent.executor import execute_plan
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="VC Research AI Agent",
    description="An AI-powered research assistant for Venture Capitalists",
    version="1.0.0"
)

# Store active research jobs
research_jobs: Dict[str, dict] = {}

class ResearchRequest(BaseModel):
    domain: str
    
class ResearchResponse(BaseModel):
    job_id: str
    message: str

class ResearchStatus(BaseModel):
    status: str
    progress: float
    results: Optional[dict] = None
    error: Optional[str] = None

@app.get("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    print(request)
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    research_jobs[job_id] = {
        "status": "planning",
        "progress": 0.0,
        "results": None,
        "error": None
    }
    
    # Add research task to background tasks
    background_tasks.add_task(
        process_research,
        job_id=job_id,
        domain=request.domain
    )
    
    return ResearchResponse(
        job_id=job_id,
        message="Research task started successfully"
    )

@app.get("/research/{job_id}", response_model=ResearchStatus)
async def get_research_status(job_id: str):
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found")
    
    return ResearchStatus(**research_jobs[job_id])

async def process_research(job_id: str, domain: str):
    try:
        # Step 1: Create research plan
        research_jobs[job_id]["status"] = "creating_plan"
        plan = await create_research_plan(domain)
        research_jobs[job_id]["progress"] = 0.2
        
        # Step 2: Validate plan
        research_jobs[job_id]["status"] = "validating_plan"
        validated_plan = await validate_plan(plan)
        research_jobs[job_id]["progress"] = 0.4
        
        # Step 3: Execute plan
        research_jobs[job_id]["status"] = "executing_plan"
        results = await execute_plan(validated_plan)
        
        # Update job status with results
        research_jobs[job_id].update({
            "status": "completed",
            "progress": 1.0,
            "results": results
        })
        
    except Exception as e:
        research_jobs[job_id].update({
            "status": "failed",
            "error": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008) 