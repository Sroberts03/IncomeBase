import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.file_review_agent import FileReviewAgent
from agents.base_agent import BaseAgent
from models.file_review_schema import BatchFileReview, IndividualFileResult
from pathlib import Path

class TestBaseAgent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.agent = BaseAgent(self.mock_client, "gpt-4", "test_agent", "v1")

    @patch("builtins.open", unittest.mock.mock_open(read_data="Hello {{ name }}"))
    @patch("pathlib.Path.parent", new_callable=MagicMock)
    def test_load_prompt_with_variables(self, mock_path):
        # Setup mock path to avoid FileNotFoundError
        mock_path.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = Path("dummy_path")
        
        # We need to mock the existence check if we use Path
        with patch("agents.base_agent.Path.parent", return_value=Path("/tmp")):
            with patch("agents.base_agent.open", unittest.mock.mock_open(read_data="Hello {{ name }}")):
                prompt = self.agent.load_prompt({"name": "World"})
                self.assertEqual(prompt, "Hello World")

    async def test_get_structured_response_text(self):
        mock_response = MagicMock()
        mock_response.choices[0].message.parsed = {"result": "success"}
        self.mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_response)

        result = await self.agent.get_structured_response("sys", "user", MagicMock())
        self.assertEqual(result, {"result": "success"})
        self.mock_client.beta.chat.completions.parse.assert_awaited_once()

class TestFileReviewAgent(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.agent = FileReviewAgent(self.mock_client)

    @patch.object(FileReviewAgent, "load_prompt", return_value="System Prompt")
    async def test_review_formats_correctly(self, mock_load_prompt):
        mock_response = MagicMock()
        expected_result = BatchFileReview(results=[], overall_summary="Ok")
        mock_response.choices[0].message.parsed = expected_result
        self.mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_response)

        images = ["img1_b64", "img2_b64"]
        file_ids = ["f1", "f2"]
        
        result = await self.agent.review(images, file_ids)
        
        self.assertEqual(result, expected_result)
        
        # Verify the call to OpenAI contains the correctly formatted vision content
        args, kwargs = self.mock_client.beta.chat.completions.parse.call_args
        user_messages = kwargs["messages"]
        
        # System message + User message
        self.assertEqual(len(user_messages), 2)
        self.assertEqual(user_messages[0]["role"], "system")
        self.assertEqual(user_messages[1]["role"], "user")
        
        content = user_messages[1]["content"]
        # text + (text + image) * 2
        self.assertEqual(len(content), 5) 
        self.assertEqual(content[1]["text"], "File ID: f1")
        self.assertEqual(content[2]["type"], "image_url")

if __name__ == "__main__":
    unittest.main()
