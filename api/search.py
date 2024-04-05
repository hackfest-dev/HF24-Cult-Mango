from duckduckgo_search import DDGS

def search(element):
    searches = [f'description of the food ingredient {element}', 
                f'{element} is good for which type of people',
                f'side-effects of the ingredient {element}', 
                f'who should avoid foods with the ingredient {element}']
    

    response = ''
    for i in range(len(searches)):
        result = DDGS().text(searches[i], max_results=1)[0]['body']
        
        if i == 0:
            response += result + ' '
        elif i == 1:
            response += f"It is beneficial for the following people to consume foods with {element}. " + result 
        elif i == 2:
            response += f" The side effects are as follows " + result
        elif i == 3:
            response += f" It should be avoided by " + result

    return response

res = search('zinc-oxide')
print(res)

        