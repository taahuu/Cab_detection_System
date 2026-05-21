"""
🚕 Cab Detection System – Interactive CLI Runner
=================================================
Entry point to run the entire ride-booking LangGraph workflow
as an interactive terminal chat session.

Usage
-----
    python run.py
"""

import sys
import uuid
import logging

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# ── Load environment variables before anything else ──────────────
load_dotenv()

# ── Logging setup ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run")

# ── Import the compiled ride graph ───────────────────────────────
from app.graph.ride_graph import ride_graph          # noqa: E402
from app.utils.helpers import format_duration_hours  # noqa: E402


# ══════════════════════════════════════════════════════════════════
#  Banner
# ══════════════════════════════════════════════════════════════════

BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚕  C A B   D E T E C T I O N   S Y S T E M  🚕          ║
║                                                              ║
║   Powered by LangGraph + OpenAI                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


# ══════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════

def print_state_update(state: dict) -> None:
    """Pretty-print key state changes after each graph step."""
    fields = [
        ("📍 Pickup",        "pickup_formatted_address"),
        ("📍 Destination",   "destination_formatted_address"),
        ("📏 Distance",      "distance_km",        " km"),
        ("⏱️  Duration",      "duration_minutes",    lambda v, s: f" {format_duration_hours(v)}"),
        ("💰 Fare",          "estimated_fare",      lambda v, s: f" {s.get('fare_currency', 'INR')} {v}"),
        ("🚗 Cab Type",      "cab_type"),
        ("👤 Driver",        "driver_name"),
        ("🚙 Vehicle",       "vehicle_number"),
        ("⏳ Driver ETA",    "driver_eta_minutes",  " min"),
        ("🛣️  Ride Status",   "ride_status"),
        ("💳 Payment",       "payment_status"),
        ("🧾 Transaction",   "transaction_id"),
    ]

    print("\n┌─── State Update ───────────────────────────────────┐")
    for entry in fields:
        label = entry[0]
        key = entry[1]
        suffix = entry[2] if len(entry) > 2 else ""

        value = state.get(key)
        if value is None:
            continue

        if callable(suffix):
            display = f"{label}: {suffix(value, state)}"
        else:
            display = f"{label}: {value}{suffix}"
        print(f"│  {display}")
    print("└────────────────────────────────────────────────────┘\n")


def print_messages(state: dict) -> None:
    """Print the latest AI message from the state."""
    messages = state.get("messages", [])
    for msg in messages:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        if role == "ai" and content.strip():
            print(f"\n🤖 Assistant: {content}\n")


# ══════════════════════════════════════════════════════════════════
#  Main – Interactive Chat Loop
# ══════════════════════════════════════════════════════════════════

def main() -> None:
    """Run the ride-booking graph interactively."""
    # Configure UTF-8 encoding for standard output and error on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    print(BANNER)

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("Welcome! I'll help you book a cab ride.")
    print("Type 'quit' or 'exit' at any time to stop.\n")

    # ── Step 0: Collect user info ────────────────────────────────
    user_name = input("👤 Enter your name: ").strip()
    if user_name.lower() in ("quit", "exit"):
        print("👋 Goodbye!")
        return
    if not user_name:
        user_name = "Guest User"

    user_phone = input("📱 Enter your phone number: ").strip()
    if user_phone.lower() in ("quit", "exit"):
        print("👋 Goodbye!")
        return
    if not user_phone:
        user_phone = "+91-99999-99999"

    # ── Step 1: Collect pickup ───────────────────────────────────
    pickup = input("\n📍 Enter your pickup location: ").strip()
    if pickup.lower() in ("quit", "exit"):
        print("👋 Goodbye!")
        return

    # ── Step 2: Collect destination ──────────────────────────────
    destination = input("📍 Enter your destination: ").strip()
    if destination.lower() in ("quit", "exit"):
        print("👋 Goodbye!")
        return

    # ── Step 3: Choose cab type ──────────────────────────────────
    print("\n🚗 Available cab types:")
    print("   1. Mini     – ₹8/km  (budget)")
    print("   2. Sedan    – ₹12/km (standard)")
    print("   3. SUV      – ₹16/km (spacious)")
    print("   4. Premium  – ₹22/km (luxury)")
    cab_choice = input("\nSelect cab type [1-4, default=2]: ").strip()
    cab_map = {"1": "mini", "2": "sedan", "3": "suv", "4": "premium"}
    cab_type = cab_map.get(cab_choice, "sedan")

    # ── Build initial input state ────────────────────────────────
    initial_input = {
        "messages": [
            HumanMessage(content=f"Pickup: {pickup}"),
            HumanMessage(content=f"Destination: {destination}"),
        ],
        "pickup_address": pickup,
        "destination_address": destination,
        "cab_type": cab_type,
        "user_name": user_name,
        "user_phone": user_phone,
    }

    print(f"\n🔄 Booking {cab_type.upper()} from '{pickup}' to '{destination}'...\n")
    print("━" * 55)

    # ── Run the graph ────────────────────────────────────────────
    try:
        # Stream through each node for live progress updates
        for event in ride_graph.stream(initial_input, config=config, stream_mode="values"):
            print_state_update(event)
            print_messages(event)

        # Check if the graph has paused at the confirm_ride breakpoint
        state = ride_graph.get_state(config)
        if state.next and "confirm_ride" in state.next:
            confirm_input = input("\n🤔 Do you want to confirm this booking? (yes/no) [default=yes]: ").strip()
            if not confirm_input:
                confirm_input = "yes"

            # Update the graph state with the user's response
            ride_graph.update_state(
                config,
                {"messages": [HumanMessage(content=confirm_input)]}
            )

            print("\n🔄 Resuming ride booking workflow...\n")
            print("━" * 55)

            # Resume graph execution
            for event in ride_graph.stream(None, config=config, stream_mode="values"):
                print_state_update(event)
                print_messages(event)

    except KeyboardInterrupt:
        print("\n\n⚠️  Ride booking interrupted by user.")
        sys.exit(0)
    except Exception as exc:
        logger.exception("Error during ride graph execution")
        print(f"\n❌ Something went wrong: {exc}")
        sys.exit(1)

    # ── Final summary ────────────────────────────────────────────
    print("━" * 55)
    try:
        final_state = ride_graph.get_state(config).values
        summary = final_state.get("ride_summary")
        if summary:
            print(f"\n{summary}\n")
        else:
            status = final_state.get("ride_status", "unknown")
            print(f"\n📋 Final ride status: {status}\n")
    except Exception:
        print("\n📋 Ride workflow finished.\n")

    print("👋 Thank you for using Cab Detection System!")


# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
