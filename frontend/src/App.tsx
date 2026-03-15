import { Routes, Route } from "react-router-dom"

import Home from "./pages/Home"
import Problems from "./pages/Problems"
import Training from "./pages/Training"
import Contest from "./pages/Contest"
import CodeAnalyzer from "./pages/CodeAnalyzer"
import Navbar from "./components/Navbar"

function App() {
  return (
    <div>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/problems" element={<Problems />} />
        <Route path="/training" element={<Training />} />
        <Route path="/contest" element={<Contest />} />
        <Route path="/code-analyzer" element={<CodeAnalyzer />} />
      </Routes>
    </div>
  )
}

export default App
