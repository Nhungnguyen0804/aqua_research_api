from src.state import LitState
from langgraph.graph import StateGraph, START, END

from PIL import Image
import io

from src.nodes.search_node  import search_node
from src.services.llm import invoke_gemini
from src.utils import get_current_time 
from src.nodes.dedup import dedup_node
from src.nodes.query_expand import query_expansion_node
'''
add_node(name, function) → đăng ký node.
add_edge(A, B) → nối từ node A sang node B.
'''


if __name__ == "__main__":
    graph_builder = StateGraph(LitState)
    graph_builder.add_node("query_expansion_node", query_expansion_node)
    graph_builder.add_edge(START, "query_expansion_node")

    graph_builder.add_node("search_node", search_node)
    graph_builder.add_edge("query_expansion_node", "search_node")

    graph_builder.add_node("dedup_node", dedup_node)
    graph_builder.add_edge('search_node','dedup_node')
    
    graph_builder.add_edge("dedup_node", END)
    lit_agent_graph = graph_builder.compile()




    png = lit_agent_graph.get_graph().draw_mermaid_png()

    img = Image.open(io.BytesIO(png))
    img.show()