from typing import Optional
from pydantic import BaseModel, ConfigDict
from ormlambda import Table, Column, ORM
from src.core import db
from src.common.misc import if_error_return


class Todo(Table):
    __table_name__ = "todo"
    id: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    item: Column[str]


class TodoModel(BaseModel):
    id: int
    item: str

    model_config = ConfigDict(from_attributes=True)


class TodoForm(BaseModel):
    item: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "item": "Element 1",
                }
            ]
        }
    }


class TodoTable:
    def __init__(self):
        self.model = ORM(Todo, db)

    @if_error_return(None)
    def insert_new_todo(self, todo_form: TodoForm) -> Optional[TodoModel]:
        todo = Todo(**todo_form.model_dump())

        self.model.insert(todo)
        return self.model.order(Todo.id, "DESC").first(flavour=TodoModel)

    @if_error_return([])
    def get_all_todos(self) -> list[TodoModel]:
        return self.model.select(flavour=TodoModel)

    @if_error_return(None)
    def get_todo_by_id(self, id: str) -> Optional[TodoModel]:
        return self.model.where(Todo.id == id).first(flavour=TodoModel)

    @if_error_return(-1)
    def update_todo(self, id, item: str) -> Optional[int]:
        return self.model.where(Todo.id == id).update({Todo.item: item})

    @if_error_return(False)
    def delete_todo_by_id(self, id) -> bool:
        self.model.where(Todo.id == id).delete()
        return True


Todos = TodoTable()
