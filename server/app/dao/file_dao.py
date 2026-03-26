import asyncio
from typing import Iterable, Dict, Any
from models.classifier_schema import SingleClassifyFile


class FileDao:
    BUCKET_NAME = "borrower-files"

    def __init__(self, supabase):
        self.supabase = supabase
    
    async def get_borrower_data_from_link_token(self, link_token: str) -> Dict[str, Any]:
        """Fetches borrower_id and zip_code associated with a link token."""
        res = await self.supabase.table("file_links") \
            .select("borrower_id, borrowers(zip_code)").eq("link_token", link_token) \
            .execute()
        if res.data and len(res.data) > 0:
            data = res.data[0]
            return {
                "borrower_id": data["borrower_id"],
                "zip_code": data["borrowers"]["zip_code"]
            }
        else:
            raise ValueError("Invalid link token")

    async def get_pending_records(self, borrower_id: str):
        res = await self.supabase.table("files") \
            .select("id, file_path") \
            .eq("borrower_id", borrower_id) \
            .eq("needs_to_be_processed", True) \
            .execute()
        return res.data or []
      
    async def get_files(self, file_paths: list[str]) -> list[bytes]:
        """Downloads multiple files from storage in parallel."""
        async def download_one(path):
            res = await self.supabase.storage.from_(self.BUCKET_NAME).download(path)
            return res.content
            
        tasks = [download_one(path) for path in file_paths]
        return await asyncio.gather(*tasks)
    
    async def update_file_classification(self, borrower_id: str, classification: SingleClassifyFile, file_id: str):
        await self.supabase.table("files").update({
            "classification": classification.classification,
            "source": classification.source,
            "file_name": classification.file_name,
            "needs_to_be_processed": False
        }).eq("id", file_id).execute()
        await self.supabase.table("reasoning_logs").insert({
            "borrower_id": borrower_id,
            "agent": "classifier",
            "raw_reasoning": classification.reasoning,
        }).execute()

    async def get_files_for_borrower(self, borrower_id: str):
        res = await self.supabase.table("files") \
            .select("*") \
            .eq("borrower_id", borrower_id) \
            .eq("needs_to_be_processed", False) \
            .execute()
        return res.data or []
    
    async def bulk_insert_line_items(self, items: Iterable[Dict[str, Any]]) -> int:
        """
        Pure DB operation: Safely chunks and inserts raw dictionaries into Supabase.
        """
        BATCH_SIZE = 1000
        current_batch = []
        total_inserted = 0
        
        for item in items:
            current_batch.append(item)
            
            if len(current_batch) == BATCH_SIZE:
                await self.supabase.table("line_items").insert(current_batch).execute()
                total_inserted += len(current_batch)
                current_batch.clear()

        # Catch remaining
        if current_batch:
            await self.supabase.table("line_items").insert(current_batch).execute()
            total_inserted += len(current_batch)

        return total_inserted
    
    async def save_analysis_results(self, analysis_results: dict, borrower_id: str):
        # 1. Merge the borrower_id into the existing dictionary
        payload = {
            "borrower_id": borrower_id,
            **analysis_results 
        }
        
        # 2. Use upsert to prevent duplicate analysis entries for the same borrower
        response = await self.supabase.table("borrower_analysis").upsert(
            payload, 
            on_conflict="borrower_id"
        ).execute()
        
        return response