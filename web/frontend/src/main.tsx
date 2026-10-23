/** 前端入口：挂载 React 根节点并引入全局样式。 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './shared/styles/index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
