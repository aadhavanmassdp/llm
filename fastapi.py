from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Todo API",
    description="A simple Todo API built with FastAPI",
    version="1.0.0"
)

# In-memory storage
todos = [
    {"id": 1, "title": "Learn FastAPI", "completed": False}
]
next_id = 2

# Pydantic models
class TodoCreate(BaseModel):
    title: str

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: int
    title: str
    completed: bool

# Routes
@app.get("/todos", response_model=List[Todo])
async def get_todos():
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todos", response_model=Todo, status_code=201)
async def create_todo(todo: TodoCreate):
    global next_id
    new_todo = {"id": next_id, "title": todo.title, "completed": False}
    todos.append(new_todo)
    next_id += 1
    return new_todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    for todo in todos:
        if todo["id"] == todo_id:
            if todo_update.title is not None:
                todo["title"] = todo_update.title
            if todo_update.completed is not None:
                todo["completed"] = todo_update.completed
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}", status_code=204)
async def delete_todo(todo_id: int):
    global todos
    todos = [todo for todo in todos if todo["id"] != todo_id]
    return {}
