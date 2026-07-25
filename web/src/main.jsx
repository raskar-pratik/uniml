import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { ToastProvider } from './context/ToastContext.jsx'
import { PipelineProvider } from './context/PipelineContext.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <PipelineProvider>
          <App />
        </PipelineProvider>
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
