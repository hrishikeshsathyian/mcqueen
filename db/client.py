import os
from supabase import create_client, Client

url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_SECRET_KEY"]

supabase: Client = create_client(supabase_url=url, supabase_key=key)
