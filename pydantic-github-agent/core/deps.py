import json
from typing import Any, Dict, List, Optional

from core.config import settings
from fastapi import HTTPException, status
from supabase import Client, create_client

# Supabase setup
supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY,
)


async def fetch_conversation_history(
    session_id: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Fetch the most recent conversation history for a session."""
    try:
        # Fetch the conversation history from the 'messages' table
        response = (
            supabase.table("messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        # Convert the response data into chronological order
        messages = response.data[::-1]  # Reversing the list to get the correct order
        return messages

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversation history: {str(e)}",
        )


async def store_message(
    session_id: str,
    message_type: str,
    content: str,
    data: Optional[Dict] = None,
):
    """Store a message in the Supabase messages table."""
    message_obj = {"type": message_type, "content": content}
    if data:
        message_obj["data"] = json.dumps(data)  # Convert dict to JSON string

    try:
        # Insert the message into the 'messages' table
        supabase.table("messages").insert(
            {"session_id": session_id, "message": message_obj}
        ).execute()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store message: {str(e)}",
        )
