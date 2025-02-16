from pydantic import BaseModel


# Request/Response Models
class AgentRequest(BaseModel):
    query: str
    user_id: str
    request_id: str
    session_id: str


class AgentResponse(BaseModel):
    success: bool
