import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function RunCreator() {
  const navigate = useNavigate();
  const [targetUrl, setTargetUrl] = useState('http://localhost:8001');
  const [apiSpec, setApiSpec] = useState('');
  const [provider, setProvider] = useState('gemini');
  const [model, setModel] = useState('gemini-3.6-flash');
  const [testCount, setTestCount] = useState(10);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        target_url: targetUrl,
        api_spec: apiSpec,
        provider,
        model,
        categories: ["functional", "negative", "validation"],
        test_count: testCount
      };
      const res = await axios.post(`${API_BASE}/runs`, payload);
      navigate(`/runs/${res.data.id}`);
    } catch (err) {
      console.error(err);
      alert('Failed to create run');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg max-w-3xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Test Run</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">Target API URL</label>
          <input type="url" required value={targetUrl} onChange={e => setTargetUrl(e.target.value)} 
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
        </div>
        
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">LLM Provider</label>
            <select value={provider} onChange={e => setProvider(e.target.value)}
              className="mt-1 block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
              <option value="gemini">Google Gemini</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Model</label>
            <input type="text" value={model} onChange={e => setModel(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Number of Tests to Generate</label>
          <input type="number" min="1" max="50" value={testCount} onChange={e => setTestCount(parseInt(e.target.value))}
            className="mt-1 block w-32 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">OpenAPI Specification (JSON or YAML)</label>
          <textarea required rows={10} value={apiSpec} onChange={e => setApiSpec(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Paste your OpenAPI 3.0 spec here..."></textarea>
        </div>

        <div className="flex justify-end">
          <button type="submit" disabled={loading}
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Run'}
          </button>
        </div>
      </form>
    </div>
  );
}
