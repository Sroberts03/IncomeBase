from typing import Any

from agents.base_agent import BaseAgent
from server.models.classifier_schema import ClassifyFile


class ClassifierAgent(BaseAgent):
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
        
        