import { useCallback, useState } from "react";
import { Todo } from "../types/todo";
import { getAllTodos } from "services/todos";


export function useTodos(){
    
    const [todo, setTodo] = useState<Todo[]>();

    const getTodos = useCallback(()=>getAllTodos(), [])



    const deleteTodos = useCallback(({})=>{}, [])
    const createTodos = useCallback(({})=>{}, [])
    
    return {
        todo,
        getTodos,
        deleteTodos,
        createTodos,

    }
}