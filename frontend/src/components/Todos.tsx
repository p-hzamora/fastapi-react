import { useEffect, useState, createContext, useCallback } from 'react'
import { Container, Stack } from '@chakra-ui/react'

import { apiClient } from '../api/apiClient'
import { Todo } from '../types/todo'
import { UserResponse } from '../types/user'

type TodosContextType = {
  todos: Todo[]
  fetchTodos: () => void
}

const TodosContext = createContext<TodosContextType>({
  todos: [],
  fetchTodos: (): void => {},
})

export default function Todos() {

  const [todos, setTodos] = useState<Todo[]>([])
  const [user, setUser] = useState<UserResponse>()

  const fetchTodos = async () => {
    const todos = await apiClient.request('todoGetAll')
    console.log(todos)
    setTodos(todos)
  }

  const getUserById = async () => {
    const user = await apiClient.request('userGetUserById', {
      params: {
        user_id: '1d20c930-bea4-4adf-a342-b60efec78f7f',
      },
    })

    console.log(user)
    setUser(user)
  }

  useEffect(() => {
    getUserById()
  }, [])

  useCallback(getUserById,[])

  useEffect(() => {
    fetchTodos()
  }, [])

  const isUserActive = user?.active

  return (
    <TodosContext.Provider value={{ todos, fetchTodos }}>
      <Container maxW="container.xl" pt="100px">
        {isUserActive && (
          <section>
            <p>Nombre de usuario: {user?.active && user.name}</p>
            <p>Imagen de usuario: {user?.active && user.profile_image_url}</p>
          </section>
        )}
        <Stack gap={5}>
          {todos.map((todo: Todo) => (
            <b key={todo.id}>{todo.item}</b>
          ))}
        </Stack>
      </Container>
    </TodosContext.Provider>
  )
}
