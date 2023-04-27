from lunr import lunr


def build_search_index():
    documents = [{
             "id": "a",
             "title": "Mr. Green kills Colonel Mustard",
             "body": """Mr. Green killed Colonel Mustard in the study with the
     candlestick. Mr. Green is not a very nice fellow."""
         }, {
             "id": "b",
             "title": "Plumb waters plant",
             "body": "Professor Plumb has a green and a yellow plant in his study",
         }, {
             "id": "c",
             "title": "Scarlett helps Professor",
             "body": """Miss Scarlett watered Professor Plumbs green plant
     while he was away on his murdering holiday.""",
         }]

    idx = lunr(
        ref='id', fields=('title', 'body'), documents=documents
    )

    return idx
