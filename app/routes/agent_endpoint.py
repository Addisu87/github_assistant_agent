import httpx
import logfire
from core.config import settings
from core.deps import fetch_conversation_history, store_message
from core.github_agent import GitHubDeps, github_agent
from core.security import verify_token
from fastapi import APIRouter, Depends
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
from schemas.assistant_agent import AgentRequest, AgentResponse

router = APIRouter()


@router.post("/api/pydantic-github-agent", response_model=AgentResponse)
async def github_agent_endpoint(
    request: AgentRequest,
    authenticated: bool = Depends(verify_token),
):
    try:
        logfire.info(f"Processing agent request: {request}")
        # Fetch conversation history for the session
        conversation_history = await fetch_conversation_history(request.session_id)

        # Convert conversation history to format expected by agent
        messages = []
        for msg in conversation_history:
            msg_data = msg["message"]
            msg_type = msg_data["type"]
            msg_content = msg_data["content"]
            msg = (
                ModelRequest(parts=[UserPromptPart(content=msg_content)])
                if msg_type == "human"
                else ModelResponse(parts=[TextPart(content=msg_content)])
            )
            messages.append(msg)

        # Store user's query
        logfire.info(f"Storing user's query: {request.query}")
        await store_message(
            session_id=request.session_id,
            message_type="human",
            content=request.query,
        )

        # Initialize agent dependencies
        async with httpx.AsyncClient() as client:
            logfire.info("Initializing agent dependencies")
            deps = GitHubDeps(client=client, github_token=settings.GITHUB_TOKEN)

            # Run the agent with conversation history
            logfire.info(
                f"Running the agent with query: {request.query} and msg: {messages}"
            )
            result = await github_agent.run(
                request.query, message_history=messages, deps=deps
            )
            logfire.info(f"Agent response: {result.data}")

        # Store agent's response
        logfire.info("Storing agent response")
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content=result.data,
            data={"request_id": request.request_id},
        )

        return AgentResponse(success=True)

    except Exception as e:
        logfire.error(f"Error processing agent request: {str(e)}")
        # Store error message in conversation
        await store_message(
            session_id=request.session_id,
            message_type="ai",
            content="I apologize, but I encountered an error processing your request.",
            data={"error": str(e), "request_id": request.request_id},
        )
        return AgentResponse(success=False)
