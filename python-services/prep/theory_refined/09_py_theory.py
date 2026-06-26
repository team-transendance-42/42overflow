
#iterable (usually a list) []
pairs = [
    {"question": "...", "answer": "...", "tags": [...]},#{}dictionary(js map)
    {"question": "...", "answer": "..."}
]

#loop over each p in pairs
#build a new list
#each iteration produces one new dictionary
#result is a list of dictionaries
augmented = [ ... for p in pairs ]

#Curly braces{} = dictionary (key-value map)
{"a": 1, "b": 2}

#“Take all key-value pairs from dictionary p and insert them here”
{
    **p,
    "_id": ...
}

#==========================
p = {"question": "Q1", "answer": "A1"}

{**p, "_id": 123}
#becomes:
{"question": "Q1", "answer": "A1", "_id": 123}

#It is a merge/clone of dicts:
#keeps original keys from p
#adds new fields (_id, _hash, _text)
#does not mutate original p