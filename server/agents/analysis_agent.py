# This agent is responsible for analyzing the financial context of a 
# borrower and providing a structured analysis result.
from agents.base_agent import BaseAgent
from models.analysis_schema import AnalysisResult

class AnalysisAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="o1",
            agent_name="analysis",
            version="v1",
            reasoning_effort="high"
        )
    async def analyze(self, financial_context: str, corrections: str = None) -> AnalysisResult:
        """Sends the prepared text summary to the AI for risk assessment."""
        prompt = self.load_prompt()
        
        user_content = f"Please perform a deep credit analysis on this borrower data:\n\n{financial_context}, and provide a structured output."

        if corrections:
            user_content += f"\n\nAlso, please take into account these corrections from the auditor:\n{corrections}"
            user_content += "\n\nIt is CRITICAL to incorporate these corrections into your final analysis."

        # Structured Output ensures the response matches your borrower_analysis table
        response = await self.get_structured_response(
            system_prompt=prompt,
            user_content=user_content,
            
            response_format=AnalysisResult
        )
        return response