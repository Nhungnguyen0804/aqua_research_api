from src.state import LitState
from langgraph.graph import StateGraph, START, END

from PIL import Image
import io

from src.nodes.search_node  import search_node

from src.nodes.dedup import dedup_node
from src.nodes.query_expand import query_expansion_node
from src.nodes.rq_pico import rq_pico_node
from src.nodes.screen_node import screen_node
from src.nodes.eligibility_node import eligibility_node, criteria_node
'''
add_node(name, function) → đăng ký node.
add_edge(A, B) → nối từ node A sang node B.
'''


if __name__ == "__main__":
    graph_builder = StateGraph(LitState)
    graph_builder.add_node('research_question_node', rq_pico_node)
    graph_builder.add_edge(START, "research_question_node")
    
    graph_builder.add_node("query_expansion_node", query_expansion_node)
    graph_builder.add_edge('research_question_node', "query_expansion_node")

    graph_builder.add_node("search_node", search_node)
    graph_builder.add_edge("query_expansion_node", "search_node")

    graph_builder.add_node("dedup_node", dedup_node)
    graph_builder.add_edge('search_node','dedup_node')
    
    graph_builder.add_node('screen_node', screen_node)
    graph_builder.add_edge('dedup_node', 'screen_node')

    graph_builder.add_node('criteria_node', criteria_node)
    graph_builder.add_edge('screen_node', 'criteria_node')

    graph_builder.add_node('eligibility_node', eligibility_node)
    graph_builder.add_edge('criteria_node', 'eligibility_node')

    graph_builder.add_edge("eligibility_node", END)
    lit_agent_graph = graph_builder.compile()




    # png = lit_agent_graph.get_graph().draw_mermaid_png()

    # img = Image.open(io.BytesIO(png))
    # img.show()


    # test
    state = {
        "topic": "Retrieval Augmented Generation",
        'research_question': None,
        "sub_queries": [],
        "raw_papers": [],
        "deduped_papers": [],
        'screened_papers':[],
        'eligibility_criteria': None,
        'eligible_papers':[]
    }

    result = lit_agent_graph.invoke(state)

    print(len(result)) # số key trong state hiện tại 