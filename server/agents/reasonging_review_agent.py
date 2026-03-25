from agents.base_agent import BaseAgent
from models.reasoning_review_schema import FinalReview

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
            response_model=FinalReview
        )
        return response