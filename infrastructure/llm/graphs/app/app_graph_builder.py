from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from infrastructure.llm.graphs.app.router_nodes import router_node
from infrastructure.llm.graphs.available_dates.availability_node import availability_node
from infrastructure.llm.graphs.booking.booking_graph import build_booking_graph
from infrastructure.llm.graphs.common.graph_state import AppState
from infrastructure.llm.graphs.fallback.fallback_node import fallback_node

def build_app_graph():
    booking_sub = build_booking_graph()

    g = StateGraph(AppState)
    g.add_node("router", router_node)
    g.add_node("booking", booking_sub)          # subgraph as node
    g.add_node("availability", availability_node)
    g.add_node("fallback", fallback_node)

    g.add_edge(START, "router")

    def branch(s: AppState) -> str:
        # priority of active subgraph
        if s.get("active_subgraph") == "booking":
            return "booking"
        # If we have booking context, continue booking
        if s.get("context") and s.get("intent") == "booking":
            return "booking"
        return s.get("intent", "unknown")

    g.add_conditional_edges(
        "router", branch,
        {
            "booking": "booking",
            "availability": "availability",
            "change": "fallback",
            "faq": "fallback",
            "unknown": "fallback",
        },
    )

    # Direct edge from booking to END - let the subgraph handle its own routing
    g.add_edge("booking", END)
    g.add_edge("availability", END)
    g.add_edge("fallback", END)

    # Add memory saver for state persistence
    memory = MemorySaver()
    return g.compile(checkpointer=memory)