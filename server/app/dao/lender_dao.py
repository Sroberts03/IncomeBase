from datetime import datetime, timezone


class LenderDao:
    def __init__(self, supabase):
        self.db = supabase

    async def get_org_id_for_lender(self, lender_id: str) -> str:
        res = await self.db.table("organization_members").select("org_id").eq("member_id", lender_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]["org_id"]
        return None

    async def create_borrower(self, lender_id: str, email: str, full_name: str, zip_code: str, 
                                org_id: str, status: str, created_at: str, updated_at: str) -> str:
        res = await self.db.table("borrowers").insert({
            "lender_id": lender_id,
            "email": email,
            "full_name": full_name,
            "zip_code": zip_code,
            "org_id": org_id,
            "status": status,
            "created_at": created_at,
            "updated_at": updated_at
        }).execute()
        
        if res.data and len(res.data) > 0:
            return res.data[0]["borrower_id"]
        raise Exception("Failed to insert borrower record.")

    async def check_borrower_ownership(self, borrower_id: str, lender_id: str) -> bool:
        """Verifies if a borrower record belongs to the calling lender."""
        res = await self.db.table("borrowers") \
            .select("borrower_id") \
            .eq("borrower_id", borrower_id) \
            .eq("lender_id", lender_id) \
            .execute()
        return len(res.data) > 0

    async def update_borrower_status(self, borrower_id: str, status: str):
        """Updates the status field for a borrower."""
        await self.db.table("borrowers") \
            .update({"status": status}) \
            .eq("borrower_id", borrower_id) \
            .execute()

    async def create_file_link(self, borrower_id: str, link_token: str, expires_at: str):
        """Inserts or updates a file link for a borrower."""
        await self.db.table("file_links").upsert({
            "borrower_id": borrower_id,
            "link_token": link_token,
            "expires_at": expires_at
        }, on_conflict="borrower_id").execute()

    async def get_borrower_by_link_token(self, link_token: str):
        """Fetches borrower details associated with a link token."""
        # Join file_links with borrowers
        res = await self.db.table("file_links") \
            .select("borrower_id, borrowers(full_name, zip_code)") \
            .eq("link_token", link_token) \
            .execute()
        
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None

    async def get_borrowers_for_org(self, org_id: str):
        """Fetches all borrowers for a given organization."""
        res = await self.db.table("borrowers") \
            .select("borrower_id, full_name, email, status, created_at") \
            .eq("org_id", org_id) \
            .order("created_at", desc=True) \
            .execute()
        return res.data or []

    async def get_dashboard_stats(self, org_id: str):
        """Fetches status counts for a given organization."""
        res = await self.db.table("borrowers") \
            .select("status") \
            .eq("org_id", org_id) \
            .execute()
        
        stats = {
            "total_borrowers": 0,
            "needs_link_creation": 0,
            "link_created": 0,
            "docs_submitted": 0,
            "completed": 0
        }
        
        if res.data:
            stats["total_borrowers"] = len(res.data)
            for row in res.data:
                status = row["status"]
                if status == "Needs Link Creation":
                    stats["needs_link_creation"] += 1
                elif status == "Link Created":
                    stats["link_created"] += 1
                elif status in ["Docs Submitted", "Analyzing"]:
                    stats["docs_submitted"] += 1
                elif status == "Analysis Completed":
                    stats["completed"] += 1
        
        return stats
    
    async def get_borrower_status(self, borrower_id: str, new_status: str = None):
        """Fetches the current status of a borrower, optionally updating it."""
        if new_status:
            await self.db.table("borrowers") \
                .update({"status": new_status}) \
                .eq("borrower_id", borrower_id) \
                .execute()
            
    async def get_borrower_details(self, borrower_id: str):
        """Fetches detailed information for a specific borrower."""
        res = await self.db.table("borrowers") \
            .select("*") \
            .eq("borrower_id", borrower_id) \
            .execute()
        return res.data[0] if res.data else None
    
    async def get_borrower_analysis(self, borrower_id: str):
        """Fetches the analysis results for a specific borrower."""
        res = await self.db.table("borrower_analysis") \
            .select("*") \
            .eq("borrower_id", borrower_id) \
            .execute()
        return res.data[0] if res.data else None

    async def get_active_document_link(self, borrower_id: str):
        """Fetches the active document upload link for a borrower, if it exists."""
        current_time = datetime.now(timezone.utc).isoformat()
        res = await self.db.table("file_links") \
            .select("link_token") \
            .eq("borrower_id", borrower_id) \
            .gt("expires_at", current_time) \
            .execute()
        return res.data[0] if res.data else None