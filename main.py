from dotenv import load_dotenv
load_dotenv()
from postgrest.types import CountMethod

from db.client import supabase

response = (
    supabase
    .table("test")
    .select("*", count=CountMethod.exact)
    .execute()
)
print(response.data)
print(response.count)

