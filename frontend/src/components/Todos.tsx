import { useEffect, useState, createContext } from 'react'
import { Container, Stack } from '@chakra-ui/react'

import { ApiClient } from '../api/apiClient'
import { API_URL, TOKEN } from '../constants'
import { Todo } from '../types/todo'

type TodosContextType = {
  todos: Todo[]
  fetchTodos: () => void
}

const TodosContext = createContext<TodosContextType>({
  todos: [],
  fetchTodos: (): void => {},
})

export default function Todos() {
  const apiClient = new ApiClient(API_URL)

  const [todos, setTodos] = useState<Todo[]>([])
  const [todo, setTodo] = useState<Todo>()
  const fetchTodos = async () => {
    const todos = await apiClient.request('todoGetAll', {
      headers: {
        "Authorization": `Bearer ${TOKEN}`,
      },
    })
    console.log(todos)
    setTodos(todos)
  }
  useEffect(() => {
    fetchTodos()
  }, [])

  return (
    <TodosContext.Provider value={{ todos, fetchTodos }}>
      <Container maxW="container.xl" pt="100px">
        <Stack gap={5}>
          {todos.map((todo: Todo) => (
            <b key={todo.id}>{todo.item}</b>
          ))}
        </Stack>
      </Container>
    </TodosContext.Provider>
  )
}
