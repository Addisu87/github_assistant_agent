from __future__ import annotations

import asyncio

from typing import List

import httpx
import logfire

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

from core.config import settings
from core.github_agent import GitHubDeps, github_agent

# Configure logfire to suppress warnings
logfire.configure(send_to_logfire="never")  # type: ignore


class CLI:
    def __init__(self):
        self.messages: List[ModelMessage] = []
        self.deps = GitHubDeps(
            client=httpx.AsyncClient(),
            github_token=settings.GITHUB_TOKEN,
        )

    async def chat(self):
        print("GitHub Agent CLI (type 'quit' to exit)")
        print("Enter your message:")

        try:
            while True:
                user_input = input("> ").strip()
                if user_input.lower() == "quit":
                    break

                # Run the agent with streaming
                result = await github_agent.run(
                    user_input, deps=self.deps, message_history=self.messages
                )

                # Store the user message
                self.messages.append(
                    ModelRequest(parts=[UserPromptPart(content=user_input)])
                )

                # Store itermediatry messages like tool calls and responses
                filtered_messages = [
                    msg
                    for msg in result.new_messages()
                    if not (
                        hasattr(msg, "parts")
                        and any(
                            part.part_kind == "user-prompt" or part.part_kind == "text"
                            for part in msg.parts
                        )
                    )
                ]
                self.messages.extend(filtered_messages)

                # Optional if you want to print out tool calls and responses
                # print(filtered_messages + "\n\n")

                print(result.data)

                # Add the final response from the agent
                self.messages.append(
                    ModelResponse(parts=[TextPart(content=result.data)])
                )
        finally:
            await self.deps.client.aclose()


async def main():
    cli = CLI()
    await cli.chat()


if __name__ == "__main__":
    asyncio.run(main())
