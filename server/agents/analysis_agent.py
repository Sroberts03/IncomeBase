# This agent is responsible for analyzing the financial context of a 
# borrower and providing a structured analysis result.
from agents.base_agent import BaseAgent
from models.analysis_schema import AnalysisResult

class AnalysisAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="gpt-4o",
            agent_name="analysis",
            version="v1"
        )
    async def analyze(self, financial_context: str) -> AnalysisResult:
        """Sends the prepared text summary to the AI for risk assessment."""
        prompt = self.load_prompt()
        
        user_content = f"Please perform a deep credit analysis on this borrower data:\n\n{financial_context}"

        # Structured Output ensures the response matches your borrower_analysis table
        response = await self.get_structured_response(
            system_prompt=prompt,
            user_content=user_content,
            response_format=AnalysisResult
        )
        return response