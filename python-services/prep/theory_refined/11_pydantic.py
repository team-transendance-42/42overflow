from pydantic import BaseModel
from fastapi import FastAPI

#Pydantic
#BaseModel:  for validating JSON data.
#Suppose client sends:

#{
#  "name": "John",
#  "age": 25
#}
app = FastAPI()
#Define a model:

class User(BaseModel):
    name: str
    age: int
    
@app.post("/users")
def create_user(user: User):
    return user