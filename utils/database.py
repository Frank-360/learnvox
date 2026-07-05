from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)


# ==========================================
# CREATE OR UPDATE USER
# ==========================================

def save_or_update_user(full_name, institution, email, filename):

    # Normalize email
    email = email.strip().lower()

    try:

        existing = (
            supabase
            .table("learnvox_users")
            .select("*")
            .eq("email", email)
            .limit(1)
            .execute()
        )

        # ------------------------------------
        # Existing user
        # ------------------------------------

        if existing.data:

            user = existing.data[0]

            documents = user.get("documents_uploaded") or 0

            response = (
                supabase
                .table("learnvox_users")
                .update({

                    "full_name": full_name,
                    "institution": institution,
                    "filename": filename,
                    "documents_uploaded": documents + 1

                })
                .eq("id", user["id"])
                .execute()
            )

            return response

        # ------------------------------------
        # New user
        # ------------------------------------

        response = (
            supabase
            .table("learnvox_users")
            .insert({

    "full_name": full_name,
    "institution": institution,
    "email": email,
    "filename": filename,

    "plan": "free",
    "subscription_status": "inactive",

    "quick_learn_used": 0,
    "deep_dive_used": 0,
    "quiz_used": 0,
    "flashcard_used": 0,

    "documents_uploaded": 1,
    "last_reset": str(date.today())

})
            .execute()
        )


        return response

    except Exception as e:

        print("Database Error:", e)
        return None

# ==========================================
# GET USER
# ==========================================

def get_user(email):

    email = email.strip().lower()

    try:

        response = (
            supabase
            .table("learnvox_users")
            .select("*")
            .eq("email", email)
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]

        return None

    except Exception as e:

        print("Database Error:", e)
        return None


# ==========================================
# UPDATE PLAN
# ==========================================

def update_plan(email, plan):

    email = email.strip().lower()

    return (
        supabase
        .table("learnvox_users")
        .update({

            "plan": plan,
            "subscription_status": "active"

        })
        .eq("email", email)
        .execute()
    )

# ==========================================
# RESET DAILY USAGE
# ==========================================

from datetime import date


def reset_daily_usage_if_needed(email):

    email = email.strip().lower()

    user = get_user(email)

    if not user:
        return

    today = str(date.today())

    if str(user.get("last_reset")) != today:

        (
            supabase
            .table("learnvox_users")
            .update({

                "quick_learn_used": 0,
                "deep_dive_used": 0,
                "quiz_used": 0,
                "flashcard_used": 0,
                "last_reset": today

            })
            .eq("email", email)
            .execute()
        )


# ==========================================
# CAN USE QUICK LEARN?
# ==========================================

def can_use_quick_learn(email):

    email = email.strip().lower()

    reset_daily_usage_if_needed(email)

    user = get_user(email)

    if not user:
        print("No user found")
        return False

    print("PLAN:", user.get("plan"))
    print("QUICK LEARN USED:", user.get("quick_learn_used"))

    if user.get("plan") == "pro":
        return True

    return (user.get("quick_learn_used") or 0) < 2

# ==========================================
# INCREMENT QUICK LEARN
# ==========================================

def increment_quick_learn(email):

    email = email.strip().lower()

    user = get_user(email)

    if not user:
        return

    used = user.get("quick_learn_used") or 0

    (
        supabase
        .table("learnvox_users")
        .update({

            "quick_learn_used": used + 1

        })
        .eq("email", email)
        .execute()
    )