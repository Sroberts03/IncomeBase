from models.classifier_schema import ClassifyFile


class FileDao:
    def __init__(self, supabase):
        self.supabase = supabase
    
    async def get_borrower_id_from_link_token(self, link_token: str) -> str:
        res = self.supabase.table("file_links").select("borrower_id").eq("link_token", link_token).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["borrower_id"]
        else:
            raise ValueError("Invalid link token")

    async def get_pending_records(self, borrower_id: str):
        res = self.supabase.table("files") \
            .select("id, file_path") \
            .eq("borrower_id", borrower_id) \
            .eq("needs_to_be_processed", True) \
            .execute()
        return res.data or []
      
    async def get_files(self, file_paths: list[str]) -> list[bytes]:
        files_bytes = []
        for path in file_paths:
            res = self.supabase.storage.from_("borrower-files").download(path)
            files_bytes.append(res.content)
        return files_bytes
    
    async def update_file_classification(self, borrower_id: str, classification: ClassifyFile, file_id: str):
        self.supabase.table("files").update({
            "classification": classification.classification,
            "source": classification.source,
            "file_name": classification.file_name,
            "needs_to_be_processed": False
        }).eq("id", file_id).execute()
        self.supabase.table("reasoning_logs").insert({
            "borrower_id": borrower_id,
            "agent": "classifier",
            "raw_reasoning": classification.reasoning,
        }).execute()