from openai import OpenAI
import os
from typing import Dict, List
import json
import asyncio
from .tools.web_search import search_companies
from .tools.web_scraper import scrape_company_info
from .tools.file_writer import write_company_profile, write_domain_summary
import boto3
import os

s3 = boto3.client("s3")
BUCKET_NAME = "aws-devops-kumar-us-east-1"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EXECUTION_PROMPT = """You are an AI research executor. Execute the following step in the research plan and provide the results:

Step:
{step}

Context:
{context}

Previous Results:
{previous_results}

Analyze the information and provide a structured response that includes:
1. Key findings
2. Relevant metrics
3. Important insights
4. Next steps or recommendations

Format the response as a JSON object."""

async def execute_plan(plan: Dict) -> Dict:
    """
    Execute a validated research plan step by step.
    
    Args:
        plan (Dict): The validated research plan
        
    Returns:
        Dict: The research results
    """
    results = {
        "companies": {},
        "domain_summary": None,
        "execution_log": []
    }
    
    context = {}
    
    try:
        for step in plan["steps"]:
            step_result = await execute_step(step, context, results)
            results["execution_log"].append({
                "step": step["name"],
                "status": "completed",
                "result": step_result
            })
            
            # Update context with step results
            context[step["name"]] = step_result
            
        # Generate final domain summary
        await generate_domain_summary(results)
        
        return results
        
    except Exception as e:
        results["execution_log"].append({
            "step": step["name"] if "step" in locals() else "unknown",
            "status": "failed",
            "error": str(e)
        })
        raise

async def execute_step(step: Dict, context: Dict, results: Dict) -> Dict:
    """
    Execute a single step of the research plan.
    
    Args:
        step (Dict): The step to execute
        context (Dict): The current execution context
        results (Dict): The current results
        
    Returns:
        Dict: The step execution results
    """
    if step["name"] == "company_identification":
        companies = await search_companies(context.get("domain_research", {}).get("domain"))
        return {"companies": companies}
        
    elif step["name"] == "company_analysis":
        for company in context.get("company_identification", {}).get("companies", []):
            company_info = await scrape_company_info(company["url"])
            results["companies"][company["name"]] = company_info
            await write_company_profile(company["name"], company_info)
        return {"analyzed_companies": list(results["companies"].keys())}
        
    else:
        # Use OpenAI to analyze and synthesize information for other steps
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert venture capital researcher."},
                {"role": "user", "content": EXECUTION_PROMPT.format(
                    step=json.dumps(step, indent=2),
                    context=json.dumps(context, indent=2),
                    previous_results=json.dumps(results, indent=2)
                )}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)

async def generate_domain_summary(results: Dict) -> None:
    """
    Generate a comprehensive domain summary based on all research results.
    
    Args:
        results (Dict): The complete research results
    """
    summary_prompt = """Based on the following research results, create a comprehensive domain summary that includes:
1. Market overview
2. Key players and their positions
3. Product trends and innovations
4. Market opportunities
5. Potential investment thesis

Research Results:
{results}

Format the response as a markdown document."""
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are an expert venture capital analyst."},
            {"role": "user", "content": summary_prompt.format(
                results=json.dumps(results, indent=2)
            )}
        ]
    )
    
    summary = response.choices[0].message.content
    await write_domain_summary(summary)
    results["domain_summary"] = summary 