from typing import List
from agents.base_agent import BaseAgent
from models.file_review_schema import BatchFileReview

class FileReviewAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="gpt-4o-mini",
            agent_name="file_review",
            version="v1"
        )
    async def review(self, images_base64: List[str]) -> BatchFileReview:
        prompt = self.load_prompt()
        
        # Start with the text instruction
        vision_content = [
            {"type": "text", "text": "Please review these documents and provide feedback for each file index."}
        ]
        
        # Loop through each image and add it to the content list with a label
        for i, img_b64 in enumerate(images_base64):
            vision_content.append({"type": "text", "text": f"File {i}:"})
            vision_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })

        # Use your structured response helper
        response = await self.get_structured_response(
            system_prompt=prompt,
            user_content=vision_content,
            response_format=BatchFileReview
        )
        return response