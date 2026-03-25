from typing import Any

from agents.base_agent import BaseAgent
from models.classifier_schema import ClassifyFile


class ClassifierAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="gpt-4o-mini",
            agent_name="classifier",
            version="v1"
        )
    async def classify(self, image_base64: str) -> ClassifyFile:
        prompt = self.load_prompt()
        vision_content = [
            {"type": "text", "text": "Please classify this document."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            }
        ] 
        response = await self.get_structured_response(
            system_prompt=prompt,
            user_content=vision_content,
            response_format=ClassifyFile
        )
        return response
        
        