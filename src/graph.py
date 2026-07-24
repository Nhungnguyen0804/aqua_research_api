from langgraph.graph import StateGraph, START, END
from src.state import LitState

from src.nodes.search_node import search_node
from src.nodes.dedup import dedup_node
from src.nodes.query_expand import query_expansion_node
from src.nodes.rq_pico import rq_pico_node
from src.nodes.screen_node import screen_node
from src.nodes.eligibility_node import eligibility_node, criteria_node
from src.nodes.extract_node import extract_node
from src.nodes.review_node import reviewer_node
from src.nodes.synthesize_node import synthesize_node
from src.nodes.report_node import report_node


def build_lit_agent_graph():
    graph_builder = StateGraph(LitState)

    # work node 
    graph_builder.add_node("research_question_node", rq_pico_node)
    graph_builder.add_node("query_expansion_node", query_expansion_node)
    graph_builder.add_node("search_node", search_node)
    graph_builder.add_node("dedup_node", dedup_node)
    graph_builder.add_node("screen_node", screen_node)
    graph_builder.add_node("criteria_node", criteria_node)
    graph_builder.add_node("eligibility_node", eligibility_node)
    graph_builder.add_node("extract_node", extract_node)
    graph_builder.add_node("reviewer_node", reviewer_node)
    graph_builder.add_node("synthesize_node", synthesize_node)
    graph_builder.add_node("report_node", report_node)

    graph_builder.add_edge(START, "research_question_node")
    graph_builder.add_edge("research_question_node", "query_expansion_node")
    graph_builder.add_edge("query_expansion_node", "search_node")
    graph_builder.add_edge("search_node", "dedup_node")
    graph_builder.add_edge("dedup_node", "screen_node")
    graph_builder.add_edge("screen_node", "criteria_node")
    graph_builder.add_edge("criteria_node", "eligibility_node")
    graph_builder.add_edge("eligibility_node", "extract_node")
    graph_builder.add_edge("extract_node", "reviewer_node")
    graph_builder.add_edge("reviewer_node", "synthesize_node")
    graph_builder.add_edge("synthesize_node", "report_node")
    graph_builder.add_edge("report_node", END)
  
    return graph_builder.compile()



lit_agent_graph = build_lit_agent_graph()