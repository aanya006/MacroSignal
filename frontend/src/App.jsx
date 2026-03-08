import { BrowserRouter, Routes, Route } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import ThemeDetailPage from './pages/ThemeDetailPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/theme/:slug" element={<ThemeDetailPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
