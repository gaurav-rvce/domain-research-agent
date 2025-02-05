from openai import OpenAI
import os
from typing import Dict
import json
from .planner import AVAILABLE_TOOLS

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VALIDATION_PROMPT = """You are an AI research plan validator. Review the following research plan and validate its completeness, feasibility, and alignment with VC research goals.

Research Plan:
{plan}

Available Tools:
{tools}

Validate the plan based on:
1. Completeness - Are all necessary steps included?
2. Tool Usage - Are the specified tools appropriate and available?
3. Dependencies - Are step dependencies properly ordered?
4. Output Quality - Will the expected outputs be sufficient for VC decision-making?
5. Feasibility - Can the plan be executed with the available tools?

If the plan is valid, return it unchanged. If modifications are needed, return the modified plan in the same JSON format with explanations for changes.

Your response should be a JSON object with:
{{
    "is_valid": boolean,
    "modifications": ["list of modifications made"],
    "modified_plan": original_or_modified_plan_object
}}"""

async def validate_plan(plan: Dict) -> Dict:
    """
    Validate and potentially modify a research plan using OpenAI's GPT model.
    
    Args:
        plan (Dict): The research plan to validate
        
    Returns:
        Dict: The validated and potentially modified plan
    """
    try:
        # Convert tools to a formatted string
        tools_str = "\n".join([f"- {name}: {desc}" for name, desc in AVAILABLE_TOOLS.items()])
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert research plan validator for venture capital analysis."},
                {"role": "user", "content": VALIDATION_PROMPT.format(
                    plan=json.dumps(plan, indent=2),
                    tools=tools_str
                )}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the validation response
        validation_result = json.loads(response.choices[0].message.content)
        
        # Validate response structure
        required_keys = {"is_valid", "modifications", "modified_plan"}
        if not all(key in validation_result for key in required_keys):
            raise ValueError("Invalid validation result structure")
        
        # If the plan is valid, return the modified plan
        return validation_result["modified_plan"]
        
    except Exception as e:
        raise Exception(f"Error validating research plan: {str(e)}")

def validate_step_dependencies(steps: list) -> bool:
    """
    Validate that step dependencies are properly ordered.
    
    Args:
        steps (list): List of steps in the plan
        
    Returns:
        bool: True if dependencies are valid
    """
    required_outputs = set()
    
    for step in steps:
        # Check if current step's requirements are met by previous steps
        if "required_outputs" in step:
            for req in step["required_outputs"]:
                if req not in required_outputs:
                    return False
        
        # Add current step's outputs to the set
        if "expected_output" in step:
            required_outputs.add(step["expected_output"])
    
    return True 