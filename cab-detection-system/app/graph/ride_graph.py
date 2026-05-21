"""
Ride Graph
==========
Assembles the full LangGraph state-machine for the cab-detection-system
ride booking workflow.

Flow
----
.. code-block:: text

    START
      │
      ▼
    collect_location
      │
      ▼
    collect_destination
      │
      ▼
    geocode_destination
      │
      ├─ (geocode failed) ──► collect_destination  (retry loop)
      │
      ▼
    calculate_distance
      │
      ▼
    calculate_fare
      │
      ▼
    search_driver
      │
      ├─ (no driver) ──► search_driver  (retry loop)
      │
      ▼
    confirm_ride
      │
      ├─ (cancelled) ──► END
      │
      ▼
    track_ride
      │
      ▼
    process_payment
      │
      ├─ (failed) ──► process_payment  (retry loop)
      │
      ▼
    complete_ride
      │
      ▼
    END
"""

import os
import logging

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from app.utils.llm_fallback import SafeChatOpenAI

# ── State ────────────────────────────────────────────────────────
from app.graph.states import RideState

# ── Nodes ────────────────────────────────────────────────────────
from app.graph.nodes.collect_location import collect_location
from app.graph.nodes.collect_destination import collect_destination
from app.graph.nodes.geocode_destination import geocode_destination
from app.graph.nodes.calculate_distance import calculate_distance
from app.graph.nodes.calculate_fare import calculate_fare
from app.graph.nodes.search_driver import search_driver
from app.graph.nodes.confirm_ride import confirm_ride
from app.graph.nodes.track_ride import track_ride
from app.graph.nodes.process_payment import process_payment
from app.graph.nodes.complete_ride import complete_ride

# ── Conditional edges ────────────────────────────────────────────
from app.graph.edges.conditional_edges import (
    route_after_geocode,
    route_after_driver_search,
    route_after_confirm,
    route_after_payment,
)

load_dotenv()

logger = logging.getLogger(__name__)

# ── LLM instance (shared across the project) ────────────────────
model = SafeChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
)


# ══════════════════════════════════════════════════════════════════
# Build the graph
# ══════════════════════════════════════════════════════════════════

def build_ride_graph() -> StateGraph:
    """Construct and compile the ride-booking LangGraph.

    Returns
    -------
    ``CompiledGraph``
        A compiled LangGraph ready to be invoked or streamed.
    """
    graph = StateGraph(RideState)

    # ── Register nodes ───────────────────────────────────────────
    graph.add_node("collect_location", collect_location)
    graph.add_node("collect_destination", collect_destination)
    graph.add_node("geocode_destination", geocode_destination)
    graph.add_node("calculate_distance", calculate_distance)
    graph.add_node("calculate_fare", calculate_fare)
    graph.add_node("search_driver", search_driver)
    graph.add_node("confirm_ride", confirm_ride)
    graph.add_node("track_ride", track_ride)
    graph.add_node("process_payment", process_payment)
    graph.add_node("complete_ride", complete_ride)

    # ── Linear edges ─────────────────────────────────────────────
    graph.add_edge(START, "collect_location")
    graph.add_edge("collect_location", "collect_destination")
    graph.add_edge("collect_destination", "geocode_destination")
    graph.add_edge("calculate_distance", "calculate_fare")
    graph.add_edge("calculate_fare", "search_driver")
    graph.add_edge("track_ride", "process_payment")
    graph.add_edge("complete_ride", END)

    # ── Conditional edges ────────────────────────────────────────
    # After geocoding → success: calculate_distance | fail: re-collect
    graph.add_conditional_edges(
        "geocode_destination",
        route_after_geocode,
        {
            "calculate_distance": "calculate_distance",
            "collect_destination": "collect_destination",
        },
    )

    # After driver search → found: confirm | not found: retry
    graph.add_conditional_edges(
        "search_driver",
        route_after_driver_search,
        {
            "confirm_ride": "confirm_ride",
            "search_driver": "search_driver",
        },
    )

    # After confirmation → confirmed: track | cancelled: end
    graph.add_conditional_edges(
        "confirm_ride",
        route_after_confirm,
        {
            "track_ride": "track_ride",
            "__end__": END,
        },
    )

    # After payment → success: complete | failed: retry
    graph.add_conditional_edges(
        "process_payment",
        route_after_payment,
        {
            "complete_ride": "complete_ride",
            "process_payment": "process_payment",
        },
    )

    # ── Compile ──────────────────────────────────────────────────
    memory = InMemorySaver()
    compiled_graph = graph.compile(
        checkpointer=memory,
        interrupt_before=["confirm_ride"]
    )

    logger.info("Ride graph compiled successfully")
    return compiled_graph


# ── Pre-built instance for easy imports ──────────────────────────
ride_graph = build_ride_graph()
