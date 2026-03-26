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