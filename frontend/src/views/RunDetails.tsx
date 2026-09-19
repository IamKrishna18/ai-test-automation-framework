import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Download, Play, Zap, FileText } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function RunDetails() {
  const { runId } = useParams<{ runId: string }>();
  const [run, setRun] = useState<any>(null);
  const [cases, setCases] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchRun = async () => {
    try {
      const res = await axios.get(`${API_BASE}/runs/${runId}`);
      setRun(res.data);
      if (res.data.status !== 'created') {
        const cRes = await axios.get(`${API_BASE}/runs/${runId}/cases`);
        setCases(cRes.data);
      }
      if (res.data.status === 'completed') {
        const rRes = await axios.get(`${API_BASE}/runs/${runId}/results`);
        setResults(rRes.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchRun();
  }, [runId]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/runs/${runId}/generate`);
      await fetchRun();
    } catch (err) {
      console.error(err);
      alert('Generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/runs/${runId}/execute`);
      await fetchRun();
    } catch (err) {
      console.error(err);
      alert('Execution failed');
    } finally {
      setLoading(false);
    }
  };

  if (!run) return <div>Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg px-6 py-4 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Run: {run.id.substring(0,8)}...</h2>
          <p className="text-sm text-gray-500 mt-1">{run.target_url} • {run.provider} • Status: {run.status}</p>
        </div>
        <div className="flex space-x-3">
          {run.status === 'created' && (
            <button onClick={handleGenerate} disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50">
              <Zap className="h-4 w-4 mr-2" />
              Generate Tests
            </button>
          )}
          {(run.status === 'generated' || run.status === 'failed') && (
            <button onClick={handleExecute} disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 disabled:opacity-50">
              <Play className="h-4 w-4 mr-2" />
              Execute Tests
            </button>
          )}
          {run.status === 'completed' && (
            <>
              <a href={`${API_BASE}/reports/${run.id}?format=html`} target="_blank"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                <FileText className="h-4 w-4 mr-2 text-gray-500" />
                HTML Report
              </a>
              <a href={`${API_BASE}/reports/${run.id}?format=csv`} target="_blank"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                <Download className="h-4 w-4 mr-2 text-gray-500" />
                CSV Export
              </a>
            </>
          )}
        </div>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Test Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Endpoint</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Validation</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Result</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {cases.map((tc) => {
              const res = results.find(r => r.test_case_id === tc.id);
              return (
                <tr key={tc.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{tc.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="font-mono bg-gray-100 px-1 py-0.5 rounded mr-2">{tc.method}</span>
                    {tc.endpoint}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {tc.validation_status === 'valid' ? (
                      <span className="text-green-600 font-semibold">Valid</span>
                    ) : (
                      <span className="text-red-600" title={tc.validation_errors}>Invalid</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {res ? (
                      <span className={`font-semibold ${res.status === 'pass' ? 'text-green-600' : 'text-red-600'}`}>
                        {res.status.toUpperCase()} ({res.actual_status_code})
                      </span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
            {cases.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                  {run.status === 'created' ? 'Click Generate Tests to create AI test cases.' : 'No tests found.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
