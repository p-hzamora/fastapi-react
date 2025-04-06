export interface Todo {
  id: number;
  item: string;
}

export interface TodoForm {
  item: string;
}

export const TODO_ENDPOINTS = {
  todoGetAll: {
    method: "GET",
    path: "/todo/",
    responseType: {} as Todo[],
    requestType: null
  },
  todoCreate: {
    method: "POST",
    path: "/todo/",
    responseType: {} as Todo,
    requestType: {} as TodoForm,
  },
  todoGetOne: {
    method: "GET",
    path: "/todo/{todo_id}",
    responseType: {} as Todo,
    paramType: {} as { todo_id: number },
  },
  todoUpdate: {
    method: "PATCH",
    path: "/todo/{todo_id}",
    responseType: {} as Todo,
    requestType: {} as TodoForm,
    paramType: {} as { todo_id: number },
  },
  todoDelete: {
    method: "DELETE",
    path: "/todo/{todo_id}",
    responseType: {} as boolean,
    paramType: {} as { todo_id: number },
  },
} as const;
