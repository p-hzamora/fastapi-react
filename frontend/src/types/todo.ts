export interface Todo {
    id: number;
    item: string;
  }
  
  export interface TodoForm {
    item: string;
  }
  
  export type TodoEndpoints = {
    "GET todo/": {
      response: Todo[];
      request: undefined;
      params: undefined;
    };
    "POST todo/": {
      response: Todo;
      request: TodoForm;
      params: undefined;
    };
    "GET todo/{todo_id}": {
      response: Todo;
      request: undefined;
      params: { todo_id: number };
    };
    "PATCH todo/{todo_id}": {
      response: Todo;
      request: TodoForm;
      params: { todo_id: number };
    };
    "DELETE todo/{todo_id}": {
      response: boolean;
      request: undefined;
      params: { todo_id: number };
    };
  };