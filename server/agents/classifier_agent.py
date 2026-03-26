# this agent is responsible for classifying documents based on their content. 
# It takes in a list of base64-encoded images and their corresponding file IDs, 
# and returns a structured response indicating the classification, source, and name for each document.
from agents.base_agent import BaseAgent
from models.classifier_schema import BatchClassifyFile


class ClassifierAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="gpt-4o-mini",
            agent_name="classifier",
            version="v1"
        )
    async def classify(self, image_base64: list[str], file_ids: list[str]) -> BatchClassifyFile:
        prompt = self.load_prompt()
        vision_content = [
            {"type": "text", "text": "Please classify these documents. Match each to the provided File ID."},
        ] 
        
        for img, f_id in zip(image_base64, file_ids):
             vision_content.extend([
                {"type": "text", "text": f"File ID: {f_id}"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                }
            ])

        response = await self.get_structured_response(
            system_prompt=prompt,
            user_content=vision_content,
            response_format=BatchClassifyFile
        )
        return response
        
        