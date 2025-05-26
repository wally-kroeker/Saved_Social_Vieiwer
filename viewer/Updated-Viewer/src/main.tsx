console.log('[main.tsx] Script Start');
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

console.log('[main.tsx] About to get root element');
const rootElement = document.getElementById("root");
console.log('[main.tsx] rootElement:', rootElement);

if (rootElement) {
  console.log('[main.tsx] Root element found, about to render App');
  createRoot(rootElement).render(<App />);
  console.log('[main.tsx] App rendering initiated');
} else {
  console.error('[main.tsx] CRITICAL: Root element with id \'root\' not found!');
}
console.log('[main.tsx] Script End');
