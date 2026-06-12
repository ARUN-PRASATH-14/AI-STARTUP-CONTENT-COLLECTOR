from supabase_client import supabase

response = supabase.table("articles").select("*").execute()

print(response.data)