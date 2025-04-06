import { ChakraProvider } from '@chakra-ui/react'
import { defaultSystem } from "@chakra-ui/react"
import Header from "./components/Header";
import Login from './components/LogIn'

function App() {

  return (
    <ChakraProvider value={defaultSystem}>
      <Header/>
      <Login/>
    </ChakraProvider>
  )
}

export default App;