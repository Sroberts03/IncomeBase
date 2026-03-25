from typing import List, Union
from agents.base_agent import BaseAgent
from models.extraction_schema import BatchExtractionResult

class ExtractionAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="gpt-4o-mini",
            agent_name="extraction",
            version="v1"
        )
    async def extract_batch(self, processed_files: list[dict]) -> BatchExtractionResult:
        prompt = self.load_prompt()
        vision_content = [{"type": "text", "text": "Extract financial data from these mixed sources."}]

        for i, file in enumerate(processed_files):
            vision_content.append({"type": "text", "text": f"File {i} context:"})
            
            if file["type"] == "text":
                # AI reads the raw text string
                vision_content.append({"type": "text", "text": file["content"]})
            else:
                # AI "looks" at the image
                vision_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{file['content']}"}
                })

        response = await self.get_structured_response(
            system_prompt=prompt,
            user_content=vision_content,
            response_format=BatchExtractionResult
        )
        return response