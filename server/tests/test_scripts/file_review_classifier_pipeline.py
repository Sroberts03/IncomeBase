import sys
import os
from pathlib import Path
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))
import asyncio
import base64
import os
from pathlib import Path
from openai import AsyncOpenAI
from agents.file_review_agent import FileReviewAgent
from agents.classifier_agent import ClassifierAgent
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def test_pipeline():
    # 1. Initialize Agents
    # Note: Use gpt-4o or gpt-4o-mini for Vision capabilities
    reviewer = FileReviewAgent(client=client, model="gpt-4o-mini", agent_name="file_review", version="v1")
    classifier = ClassifierAgent(client=client, model="gpt-4o-mini", agent_name="classifier", version="v1")

    # 2. Collect all test images from the directory
    test_dir = Path("tests/test_docs")
    image_extensions = [".jpg", ".jpeg", ".png"]
    
    # This list will hold our base64 strings
    images_base64 = []
    # This list will keep track of filenames so we can print them later
    filenames = []

    for file_path in test_dir.iterdir():
        if file_path.suffix.lower() in image_extensions:
            with open(file_path, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode("utf-8")
                images_base64.append(encoded_string)
                filenames.append(file_path.name)

    if not images_base64:
        print("❌ No images found in tests/test_docs/")
        return

    # 3. Step 1: Run BATCH File Review (One API call for all docs)
    print(f"🚀 Sending {len(images_base64)} files for Batch Review...")
    batch_review = await reviewer.review(images_base64)
    
    # 4. Step 2: Process Results
    for res in batch_review.results:
        # We use res.file_index to map the result back to our filename
        current_filename = filenames[res.file_index]
        print(f"\n--- Result for: {current_filename} ---")
        print(f"Status: {res.status.upper()}")
        print(f"Message: {res.borrower_message}")
        
        # 5. Step 3: Classify only if approved
        if res.status == "approved":
            print(f"🔍 Document approved. Running Classifier for {current_filename}...")
            # We pass the specific image data from our list to the classifier
            class_result = await classifier.classify(images_base64[res.file_index])
            print(f"Classification: {class_result.classification}")
            print(f"Source: {class_result.source}")
        else:
            print(f"🛑 Skipping Classification for {current_filename}.")

if __name__ == "__main__":
    asyncio.run(test_pipeline())