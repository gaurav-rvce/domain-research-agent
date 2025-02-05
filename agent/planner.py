from openai import OpenAI
import os
from typing import List, Dict
import json
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

PLANNING_PROMPT = """You are an AI research planner for a Venture Capitalist. Create a detailed step-by-step plan to research the following domain: {domain}

The plan should include:
1. Initial domain research and market analysis
2. Company identification and filtering
3. Detailed company analysis for each identified company
4. Product line investigation
5. Financial metrics gathering
6. Summary and opportunity analysis

For each step, specify:
- The objective
- Required tools/APIs
- Expected output
- Success criteria

Format the response as a JSON object with the following structure:
{{
    "steps": [
        {{
            "name": "step_name",
            "objective": "step_objective",
            "tools": ["tool1", "tool2"],
            "expected_output": "output_description",
            "success_criteria": "criteria_description"
        }}
    ]
}}"""

async def create_research_plan(domain: str) -> Dict:
    """
    Create a detailed research plan using OpenAI's GPT model.
    
    Args:
        domain (str): The domain to research
        
    Returns:
        Dict: A structured research plan
    """
    plan = ""
    try:
        # message = PLANNING_PROMPT.format(domain=domain)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert research planner for venture capital analysis."},
                {"role": "user", "content": PLANNING_PROMPT.format(domain=domain)}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response into a Python dictionary
        plan = json.loads(response.choices[0].message.content)
        print(plan)
        # Validate plan structure
        if not isinstance(plan, dict) or "steps" not in plan:
            raise ValueError("Invalid plan structure received from OpenAI")
        
        return plan
        
    except Exception as e:
        print(f"Error creating research plan: {str(e)}")
        raise Exception(f"Error creating research plan: {plan}")

# Available research tools
AVAILABLE_TOOLS = {
    "web_search": "Search the internet for relevant information",
    "company_scraper": "Extract information from company websites",
    "financial_data": "Gather financial metrics and valuations",
    "market_analysis": "Analyze market trends and opportunities",
    "document_writer": "Create formatted markdown documents"
} 