import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Activity, LayoutDashboard } from 'lucide-react';

// Placeholders for views we'll build
import Dashboard from './views/Dashboard';
import RunCreator from './views/RunCreator';
import RunDetails from './views/RunDetails';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <Activity className="h-8 w-8 text-indigo-600" />
                  <span className="ml-2 text-xl font-bold text-gray-900">AI Test Framework</span>
                </div>
                <nav className="ml-6 flex space-x-8">
                  <Link to="/" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    <LayoutDashboard className="h-4 w-4 mr-1" />
                    Dashboard
                  </Link>
                  <Link to="/runs/new" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                    New Run
                  </Link>
                </nav>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/runs/new" element={<RunCreator />} />
            <Route path="/runs/:runId" element={<RunDetails />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
