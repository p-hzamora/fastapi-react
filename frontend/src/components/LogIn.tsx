import { useLogin } from '../hooks/useLogin'
import { FormEvent, useState } from 'react'
import { SessionUserResponse } from '../types/auth'

export default function LogIn() {
  const [username, setUsername] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [user, setUser] = useState<SessionUserResponse>()

  const { isLoading, error, setError, getUser, setIsLoading } = useLogin()

  const validateForm = (): boolean => {
    if (!username || !password) {
      setError('Username or Password are required')
      return false
    }
    return true
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!validateForm()) return
    setIsLoading(true)
    setUser(await getUser({email:username, password}))
  }

  return (
    <>
      <div>
        <form onSubmit={handleSubmit}>
          <label>Email</label>
          <input
            autoFocus
            required
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <label>Password</label>
          <input
            required
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Log in</button>
        </form>

        {error}
      </div>
    </>
  )
}
