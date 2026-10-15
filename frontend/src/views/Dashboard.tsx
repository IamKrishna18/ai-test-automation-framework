import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Play, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [runs, setRuns] = useState<any[]>([]);

  useEffect(() => {
    // Fetch stats
    axios.get(`${API_BASE}/dashboard/stats`).then(res => setStats(res.data)).catch(console.error);
    // Fetch recent runs
    axios.get(`${API_BASE}/runs?limit=5`).then(res => setRuns(res.data.runs)).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border-t-4 border-indigo-500">
          <h3 className="text-sm font-medium text-gray-500">Total Runs</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats?.total_runs || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border-t-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-500">Tests Generated</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats?.total_tests_generated || 0}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6 border-t-4 border-green-500">
          <h3 className="text-sm font-medium text-gray-500">Overall Pass Rate</h3>
          <p className="mt-2 text-3xl font-bold text-gray-900">{stats?.overall_pass_rate || 0}%</p>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 border-b border-gray-200 sm:px-6 flex justify-between items-center">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Test Runs</h3>
          <div className="flex space-x-3">
            <Link to="/runs/new?demo=true" className="inline-flex items-center px-3 py-2 border border-indigo-600 text-sm font-medium rounded-md text-indigo-600 bg-white hover:bg-indigo-50 transition shadow-sm">
              <Play className="h-4 w-4 mr-1.5 text-indigo-600" />
              Try 1-Click Demo
            </Link>
            <Link to="/runs/new" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 transition">
              New Run
            </Link>
          </div>
        </div>
        <ul className="divide-y divide-gray-200">
          {runs.map((run) => (
            <li key={run.id}>
              <Link to={`/runs/${run.id}`} className="block hover:bg-gray-50 px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium text-indigo-600 truncate">
                    {run.target_url} <span className="text-gray-500 text-xs ml-2">({run.provider} / {run.model})</span>
                  </div>
                  <div className="ml-2 flex-shrink-0 flex">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${run.status === 'completed' ? 'bg-green-100 text-green-800' : 
                        run.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {run.status}
                    </span>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex text-sm text-gray-500 space-x-4">
                    <span className="flex items-center"><CheckCircle className="flex-shrink-0 mr-1.5 h-4 w-4 text-green-500"/> {run.passed}</span>
                    <span className="flex items-center"><XCircle className="flex-shrink-0 mr-1.5 h-4 w-4 text-red-500"/> {run.failed}</span>
                    <span className="flex items-center"><AlertTriangle className="flex-shrink-0 mr-1.5 h-4 w-4 text-yellow-500"/> {run.errors}</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                    <p>{new Date(run.created_at).toLocaleString()}</p>
                  </div>
                </div>
              </Link>
            </li>
          ))}
          {runs.length === 0 && (
            <li className="px-4 py-8 text-center text-gray-500">No test runs yet. Create one!</li>
          )}
        </ul>
      </div>
    </div>
  );
}
