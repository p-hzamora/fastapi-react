from fastapi import APIRouter, Depends, HTTPException, status
from src.core.constants import ERROR_MESSAGES

from src.domain.auth import get_verified_user
from src.domain.todos import Todos, TodoModel, TodoForm

router = APIRouter(dependencies=[Depends(get_verified_user)])


@router.get("/", response_model=list[TodoModel])
async def get_all_todos():
    return Todos.get_all_todos()


@router.get("/{todo_id}", response_model=TodoModel)
async def get_todo(todo_id: int) -> TodoModel:
    return Todos.get_todo_by_id(todo_id)


@router.patch("/{todo_id}", response_model=TodoModel)
async def update_todo(todo_id: int, todo: TodoForm) -> TodoModel:
    Todos.update_todo(todo_id, item=todo.item)
    return Todos.get_todo_by_id(todo_id)


@router.post("/", response_model=TodoModel)
async def insert_todo(todo: TodoForm) -> TodoModel:

    inserted_todo = Todos.insert_new_todo(todo)

    if not inserted_todo:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.DEFAULT("There was an error while inserting new todo.")
        )

    return inserted_todo


@router.delete("/{todo_id}", response_model=bool)
async def delete_todo(todo_id: int) -> bool:
    return Todos.delete_todo_by_id(todo_id)
