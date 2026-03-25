import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Path setup for imports
import sys
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from agents.extraction_agent import ExtractionAgent
from app.utils.document_parser import DocumentParser

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def test_extraction():
    agent = ExtractionAgent(client=client)
    test_dir = Path("tests/test_docs")
    
    # 1. Use the Parser to build the payload
    payload = []
    for file_path in test_dir.iterdir():
        parsed_file = DocumentParser.parse(file_path)
        if parsed_file:
            payload.append(parsed_file)

    print(f"🚀 Extractor Agent starting on {len(payload)} files...")

    # 2. Call the Agent
    # Make sure your ExtractionAgent.extract_batch method accepts this list of dicts!
    result = await agent.extract_batch(payload)

    # 3. Print the results
    for res in result.results:
        print(f"\n--- {payload[res.file_index]['name']} ---")
        print(f"Institution: {res.extracted_data.institution}")
        print(f"Reasoning: {res.reasoning}")
        
        for item in res.extracted_data.line_items:
            icon = "💰" if item.is_income else "💸"
            print(f"  {icon} {item.file_date} | {item.description[:30]:<30} | ${item.amount}")

if __name__ == "__main__":
    asyncio.run(test_extraction())