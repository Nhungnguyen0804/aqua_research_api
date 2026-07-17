from src.nodes import search_node

state = {
    "query": "Drug Discovery"
}

result = search_node(state)

print(len(result["raw_papers"]))
print(result["raw_papers"][0])