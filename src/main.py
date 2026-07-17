from src.state import LitState
from langgraph.graph import StateGraph, START, END

from src.nodes.search_node  import search_node
from src.services.llm import invoke_gemini
from src.utils import get_current_time 

if __name__ == "__main__":
    graph_builder = StateGraph(LitState)
    graph_builder.add_node("search_node", search_node)
    graph_builder.add_edge(START, "search_node")
    graph_builder.add_edge("search_node", END)
    basic_agent_graph = graph_builder.compile()


from PIL import Image
import io

png = basic_agent_graph.get_graph().draw_mermaid_png()

img = Image.open(io.BytesIO(png))
img.show()