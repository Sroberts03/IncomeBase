# This agent is responsible for extracting financial data from documents.
# It takes in a processed file (either text or image), 
# along with its file ID and name, and returns a structured response containing the extracted financial data.
from typing import List, Union
from agents.base_agent import BaseAgent
from models.extraction_schema import IndividualFileExtraction

class ExtractionAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="gpt-4o-mini",
            agent_name="extraction",
            version="v1"
        )
    async def extract_single_file(self, processed_file: dict, file_id: str, file_name: str) -> IndividualFileExtraction:
        prompt = self.load_prompt()
        vision_content = [{"type": "text", "text": "Extract financial data from this document."}]
        vision_content.append({"type": "text", "text": f"File id: {file_id} file name: {file_name} context:"})
            
        if processed_file["type"] == "text":
            # AI reads the raw text string
            vision_content.append({"type": "text", "text": processed_file["content"]})
        else:
                # AI "looks" at the image
                vision_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{processed_file['content']}"}
                })

        response = await self.get_structured_response(
            system_prompt=prompt,
            user_content=vision_content,
            response_format=IndividualFileExtraction
        )
        return response