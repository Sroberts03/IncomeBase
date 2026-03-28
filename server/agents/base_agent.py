from typing import Any, Dict

from openai import AsyncOpenAI
import os
from pathlib import Path

class BaseAgent:
    def __init__(self, client: AsyncOpenAI, model: str, agent_name: str, version: str, reasoning_effort: str = None):
        self.client = client
        self.model = model
        self.agent_name = agent_name
        self.version = version
        self.reasoning_effort = reasoning_effort

    # This helper makes it easy for every agent to call OpenAI with Structured Outputs
    async def get_structured_response(self, system_prompt: str, user_content: Any, response_format: Any):
        """
        Handles both text strings and multi-modal content (images/files).
        user_content can be a str or a list of dicts for Vision.
        """
        # If it's just a string, we wrap it in the standard format
        if isinstance(user_content, str):
            user_messages = [{"role": "user", "content": user_content}]
        else:
            # If you passed a pre-formatted list (for Vision/Images), use it directly
            user_messages = [{"role": "user", "content": user_content}]
        if self.reasoning_effort:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *user_messages
                ],
                response_format=response_format,
                reasoning_effort=self.reasoning_effort
            )
        else:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *user_messages
                ],
                response_format=response_format,
            )
        return response.choices[0].message.parsed

    def load_prompt(self, variables: Dict[str, str] = None) -> str:
        """Loads a prompt string from the prompts directory."""
        # This finds the absolute path to the 'prompts' folder relative to this file
        current_dir = Path(__file__).parent
        prompt_path = current_dir / "prompts" / self.agent_name / f"{self.version}_prompt.txt"
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                
                # Simple injection logic for things like {{ name }}
                if variables:
                    for key, value in variables.items():
                        content = content.replace(f"{{{{ {key} }}}}", str(value))
                return content
        except FileNotFoundError:
            print(f"⚠️ Warning: Prompt file {self.version}_prompt.txt not found.")
            return ""