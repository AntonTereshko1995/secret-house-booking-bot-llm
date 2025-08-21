from langgraph.graph import StateGraph, START, END
from infrastructure.llm.graphs.app.router_nodes import router_node
from infrastructure.llm.graphs.available_dates.availability_node import availability_node
from infrastructure.llm.graphs.booking.booking_graph import build_booking_graph
from infrastructure.llm.graphs.booking.booking_nodes import booking_exit_node
from infrastructure.llm.graphs.common.checkpoint_store import create_checkpointer
from infrastructure.llm.graphs.common.graph_state import AppState
from infrastructure.llm.graphs.fallback.fallback_node import fallback_node

def build_app_graph():
    booking_sub = build_booking_graph()

    g = StateGraph(AppState)
    g.add_node("router", router_node)
    g.add_node("booking", booking_sub)          # subgraph as node
    g.add_node("availability", availability_node)
    g.add_node("fallback", fallback_node)
    g.add_node("booking_exit", booking_exit_node)

    g.add_edge(START, "router")

    def branch(s: AppState) -> str:
        # priority of active subgraph
        if s.get("active_subgraph") == "booking":
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

    g.add_edge("booking", "booking_exit")
    g.add_edge("booking_exit", END)
    g.add_edge("availability", END)
    g.add_edge("fallback", END)

    return g.compile(checkpointer=create_checkpointer)