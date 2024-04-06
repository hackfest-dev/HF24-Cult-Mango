from duckduckgo_search import DDGS


def search(element) -> str:
    searches = [
        f'description of the food ingredient {element}',
        f'{element} is good for which type of people',
        f'side-effects of the ingredient {element}',
        f'who should avoid foods with the ingredient {element}'
    ]
    response = DDGS().text(searches[0], max_results=1)[0]['body']
    response += f"\nIt is beneficial for the following people to consume foods with {DDGS().text(searches[1], max_results=1)[0]['body']}\n"
    response += f"\nThe side effects are as follows {DDGS().text(searches[2], max_results=1)[0]['body']}\n"
    response += f"\nIt should be avoided by {DDGS().text(searches[3], max_results=1)[0]['body']}\n"
    return response
