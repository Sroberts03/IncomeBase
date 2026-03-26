import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
# agents
from agents.file_review_agent import FileReviewAgent
from agents.classifier_agent import ClassifierAgent
from agents.extraction_agent import ExtractionAgent
from agents.analysis_agent import AnalysisAgent
from agents.reasoning_review_agent import ReasoningReviewAgent

# file
from app.handlers.file_handlers import FileHandler
from app.services.file_services import FileService
from app.dao.file_dao import FileDao

# supabase
from supabase import create_client, Client

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

class AppContainer:
    """Holds single instances of our core logic classes."""
    def __init__(self):
        self.ai_client = client
        self.supabase = supabase
        self.file_review_agent = None
        self.classifier_agent = None
        self.extraction_agent = None
        self.analysis_agent = None
        self.reasoning_review_agent = None
        self.file_dao = None
        self.file_service = None
        self.file_handler = None

    def initialize(self):
        # agents
        self.file_review_agent = FileReviewAgent(client=self.ai_client)
        self.classifier_agent = ClassifierAgent(client=self.ai_client)
        self.extraction_agent = ExtractionAgent(client=self.ai_client)
        self.analysis_agent = AnalysisAgent(client=self.ai_client)
        self.reasoning_review_agent = ReasoningReviewAgent(client=self.ai_client)

        # files
        self.file_dao = FileDao(supabase=self.supabase)
        self.file_service = FileService(
            file_dao=self.file_dao,
            file_review_agent=self.file_review_agent,
            classifier_agent=self.classifier_agent
        )
        self.file_handler = FileHandler(service=self.file_service)

container = AppContainer()