"""
Collect Destination Node
========================
Prompts the user for their destination address using the LLM
and stores it in the graph state.
"""

import os
import logging
from typing import Any

from app.utils.llm_fallback import SafeChatOpenAI
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

model = SafeChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)


def collect_destination(state: dict[str, Any]) -> dict[str, Any]:
    """LangGraph node: extract the destination address from user messages.

    The LLM parses the conversation to identify the destination,
    then stores the raw address string for geocoding downstream.

    Reads
    -----
    - ``state["destination_address"]`` – if already provided.
    - ``state["geocode_status"]``      – geocode status (to check if retry is needed).
    - ``state["messages"]``            – full conversation so far.

    Writes
    ------
    - ``destination_address`` – the extracted destination address string.
    - ``messages``            – appended assistant message confirming the destination.
    """
    destination = state.get("destination_address", "").strip()
    geocode_status = state.get("geocode_status")

    # If destination is already set and geocoding hasn't failed, reuse it
    if destination and geocode_status not in ("geocoding_failed", "error"):
        logger.info("Destination address already in state: '%s'. Reusing it.", destination)
        return {
            "destination_address": destination,
        }

    messages = state.get("messages", [])

    system_prompt = SystemMessage(
        content=(
            "You are a cab-booking assistant. The user has already provided "
            "their pickup location. Now extract the DESTINATION address from "
            "the conversation. Reply with ONLY the destination address as a "
            "single line — nothing else. If no destination is mentioned, ask "
            "the user: 'Where would you like to go?'"
        )
    )

    logger.info("Extracting destination from conversation using SafeChatOpenAI")
    response = model.invoke([system_prompt] + messages)
    destination = response.content.strip()

    logger.info("Extracted destination: %s", destination)

    return {
        "destination_address": destination,
        "messages": [response],
    }
