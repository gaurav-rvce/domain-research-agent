from typing import Dict
import os
import json
from datetime import datetime
import boto3
import os

# Read S3 bucket name from environment variable
BUCKET_NAME = os.getenv("S3_BUCKET")

if not BUCKET_NAME:
    raise ValueError("S3_BUCKET environment variable is not set.")

# Initialize S3 client
s3 = boto3.client("s3")

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
    Write the domain summary to a local file and upload it to S3.

    Args:
        summary (str): The domain summary content.
    """
    try:
        # Create local output directory if it doesn't exist
        os.makedirs("research_output", exist_ok=True)

        filename = "research_output/domain_summary.md"

        # Add timestamp to summary
        content = f"{summary}\n\n---\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"

        # Write to local file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Domain summary saved locally: {filename}")

        # Upload to S3
        s3_key = "domain_summary.md"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=content.encode("utf-8"),
            ContentType="text/markdown"
        )

        print(f"Domain summary uploaded to S3: s3://{BUCKET_NAME}/{s3_key}")

    except FileNotFoundError as e:
        print(f"Error: Directory not found - {e}")
    except boto3.exceptions.Boto3Error as e:
        print(f"Error uploading to S3 - {e}")
    except Exception as e:
        print(f"Unexpected error writing domain summary: {e}")


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