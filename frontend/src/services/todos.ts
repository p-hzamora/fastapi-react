
import { apiClient } from "api/apiClient";

export const getAllTodos = async () => {
    return await apiClient.request("todoGetAll")
}

export const getTodo = async (todo_id: number) => {
    return await apiClient.request("todoGetOne", {
        params: { todo_id: todo_id }
    })
}

export const todoInsert = async (item: string) => {
    return await apiClient.request("todoCreate", { body: { item } })
}

export const todoDelete = async (todo_id: number) => {
    return await apiClient.request("todoDelete", { params: { todo_id } })
}