from src.state import LitState
from src.nodes.search_node  import search_node
if __name__ == "__main__":
    state: LitState = {
        'query': 'diffusion model evaluation'

    }

    state = search_node(state)
    print('Tìm đc: ',len(state['raw_papers']))