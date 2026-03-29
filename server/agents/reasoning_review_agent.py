# This agent is responsible for reviewing the AI's financial analysis
#  by comparing it against the raw financial data.
# It takes in the raw financial context and 
# the AI's analysis output, and returns a structured
from agents.base_agent import BaseAgent
from models.reasoning_review_schema import FinalReview

class ReasoningReviewAgent(BaseAgent):
    def __init__(self, client):
        super().__init__(
            client=client,
            model="gpt-4o",
            agent_name="reasoning_review",
            version="v1",
        )
    async def review_analysis(self, raw_context: str, analysis_output: str) -> FinalReview:
            """
            Compares the raw financial data against the AI's analysis 
            to catch hallucinations or missed risks.
            """
            prompt = self.load_prompt()
            
            # We give the Auditor BOTH the facts and the interpretation
            user_content = (
                f"### RAW FINANCIAL DATA:\n{raw_context}\n\n"
                f"### AGENT ANALYSIS TO AUDIT:\n{analysis_output}"
            )

            response = await self.get_structured_response(
                system_prompt=prompt,
                user_content=user_content,
                response_format=FinalReview
            )
            return response