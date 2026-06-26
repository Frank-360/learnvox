from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

def save_user(full_name, institution, email, filename):

    data = {
        "full_name": full_name,
        "institution": institution,
        "email": email,
        "filename": filename
    }

    try:
        response = (
            supabase
            .table("learnvox_users")
            .insert(data)
            .execute()
        )
        return response

    except Exception as e:
        print(f"Database Error: {e}")
        return None