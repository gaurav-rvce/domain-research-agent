from typing import Dict
import os
import json
from datetime import datetime

COMPANY_PROFILE_TEMPLATE = """# {company_name}

## Company Overview
{company_overview}

## Product Lines
{product_lines}

## Market Position
{market_position}

## Technology Stack
{tech_stack}

## Key Differentiators
{differentiators}

## Target Customers
{target_customers}

## Financial Information
{financials}

---
*Generated on {date}*
"""

async def write_company_profile(company_name: str, company_info: Dict) -> None:
    """
    Write company information to a markdown file.
    
    Args:
        company_name (str): Name of the company
        company_info (Dict): Company information to write
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs("research_output", exist_ok=True)
        
        # Clean company name for filename
        clean_name = "".join(c if c.isalnum() else "_" for c in company_name)
        filename = f"research_output/{clean_name}.md"
        
        # Format company information
        content = COMPANY_PROFILE_TEMPLATE.format(
            company_name=company_name,
            company_overview=company_info.get("company_overview", "Information not available"),
            product_lines=format_product_lines(company_info.get("product_lines", [])),
            market_position=company_info.get("market_positioning", "Information not available"),
            tech_stack=format_tech_stack(company_info.get("technology_stack", [])),
            differentiators=format_list(company_info.get("key_differentiators", [])),
            target_customers=company_info.get("target_customers", "Information not available"),
            financials=format_financials(company_info.get("revenue_valuation", {})),
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Write to file
        with open(filename, "w") as f:
            f.write(content)
            
    except Exception as e:
        raise Exception(f"Error writing company profile: {str(e)}")

async def write_domain_summary(summary: str) -> None:
    """
    Write domain summary to a markdown file.
    
    Args:
        summary (str): The domain summary to write
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs("research_output", exist_ok=True)
        
        filename = f"research_output/domain_summary.md"
        
        # Add timestamp to summary
        content = f"{summary}\n\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        # Write to file
        with open(filename, "w") as f:
            f.write(content)
            
    except Exception as e:
        raise Exception(f"Error writing domain summary: {str(e)}")

def format_product_lines(product_lines: list) -> str:
    """Format product lines as markdown."""
    if not product_lines:
        return "Information not available"
        
    result = ""
    for product in product_lines:
        if isinstance(product, dict):
            result += f"### {product.get('name', 'Unnamed Product')}\n"
            result += f"{product.get('description', '')}\n\n"
            if 'features' in product:
                result += "**Features:**\n"
                for feature in product['features']:
                    result += f"- {feature}\n"
                result += "\n"
        else:
            result += f"- {product}\n"
    
    return result

def format_tech_stack(tech_stack: list) -> str:
    """Format technology stack as markdown."""
    if not tech_stack:
        return "Information not available"
        
    return "\n".join(f"- {tech}" for tech in tech_stack)

def format_list(items: list) -> str:
    """Format a list as markdown bullet points."""
    if not items:
        return "Information not available"
        
    return "\n".join(f"- {item}" for item in items)

def format_financials(financials: Dict) -> str:
    """Format financial information as markdown."""
    if not financials:
        return "Information not available"
        
    result = ""
    if "revenue" in financials:
        result += f"**Revenue:** {financials['revenue']}\n"
    if "valuation" in financials:
        result += f"**Valuation:** {financials['valuation']}\n"
    if "funding" in financials:
        result += f"**Funding:** {financials['funding']}\n"
        
    return result or "Information not available" 