import asyncio
from app.core.container import __Container__
container = __Container__()

async def main():
    sb = await container.supabase_client()
    # List a few rows from borrowers
    b = await sb.table("borrowers").select("lender_id, email").limit(1).execute()
    print("Borrower:", b.data)
    
    if b.data:
        lender_id = b.data[0]['lender_id']
        try:
            # Try fetching from auth.users (won't work if anon key unless RLS allows)
            res = sb.auth.admin.get_user_by_id(lender_id)
            print("Lender email:", res.user.email)
        except Exception as e:
            print("Error getting auth user:", e)
            print("Looking for another table...")
            tables = await sb.rpc("get_schema_tables").execute()
            print(tables)

asyncio.run(main())
