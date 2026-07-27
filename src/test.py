from src.graph import lit_agent_graph 
'''
add_node(name, function) → đăng ký node.
add_edge(A, B) → nối từ node A sang node B.
'''


if __name__ == "__main__":
    # test
    state = {
        "topic": "Retrieval Augmented Generation",
        'pico': None,
        "sub_queries": [],
        "raw_papers": [],
        "deduped_papers": [],
        'screened_papers':[],
        'eligibility_criteria': None,
        'eligible_papers':[],
        'included_papers':[],
        'reviewed_papers':[],
        'synthesis':None,
        'report_content': None,
    }

    result = lit_agent_graph.invoke(state)

    print(len(result)) # số key trong state hiện tại 