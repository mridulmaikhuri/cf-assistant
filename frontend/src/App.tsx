import { Routes, Route } from "react-router-dom"

import Problems from "./pages/Problems"

function App() {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Problems />} />
      </Routes>
    </div>
  )
}

export default App
