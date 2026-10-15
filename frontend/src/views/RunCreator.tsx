import { useState, useEffect, type FormEvent } from 'react';
import axios from 'axios';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Sparkles, CheckCircle2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const DEMO_SPEC = {
  openapi: "3.0.3",
  info: {
    title: "Sample Target API",
    version: "1.0.0",
    description: "Built-in target API for automated AI test generation and execution"
  },
  servers: [{ url: "http://localhost:8001" }],
  paths: {
    "/users": {
      get: {
        summary: "List all users",
        parameters: [{ name: "limit", in: "query", schema: { type: "integer" } }],
        responses: { "200": { description: "Success" } }
      },
      post: {
        summary: "Create a user",
        requestBody: {
          required: true,
          content: {
            "application/json": {
              schema: {
                type: "object",
                properties: {
                  name: { type: "string" },
                  email: { type: "string" },
                  age: { type: "integer" }
                },
                required: ["name", "email", "age"]
              }
            }
          }
        },
        responses: {
          "201": { description: "User created" },
          "400": { description: "Validation error" },
          "422": { description: "Missing fields" }
        }
      }
    },
    "/users/{user_id}": {
      get: {
        summary: "Get user by ID",
        parameters: [{ name: "user_id", in: "path", required: true, schema: { type: "integer" } }],
        responses: {
          "200": { description: "User found" },
          "400": { description: "Invalid user ID" },
          "404": { description: "User not found" },
          "500": { description: "Internal Server Error" }
        }
      }
    },
    "/products": {
      get: {
        summary: "List inventory products",
        responses: { "200": { description: "Product list" } }
      }
    }
  }
};

export default function RunCreator() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [targetUrl, setTargetUrl] = useState('http://localhost:8001');
  const [apiSpec, setApiSpec] = useState('');
  const [provider, setProvider] = useState('gemini');
  const [model, setModel] = useState('gemini-3.6-flash');
  const [testCount, setTestCount] = useState(10);
  const [loading, setLoading] = useState(false);
  const [demoLoaded, setDemoLoaded] = useState(false);

  const loadDemoSpec = () => {
    setTargetUrl('http://localhost:8001');
    setApiSpec(JSON.stringify(DEMO_SPEC, null, 2));
    setProvider('mock');
    setModel('mock-standard');
    setTestCount(4);
    setDemoLoaded(true);
  };

  useEffect(() => {
    if (searchParams.get('demo') === 'true') {
      loadDemoSpec();
    }
  }, [searchParams]);

  const handleSubmit = async (e: FormEvent) => {
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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-gray-200 mb-6 gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Create New Test Run</h2>
          <p className="text-sm text-gray-500 mt-1">Configure an automated test run against any OpenAPI 3.0 target</p>
        </div>
        <button
          type="button"
          onClick={loadDemoSpec}
          className="inline-flex items-center px-4 py-2 border border-indigo-600 rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          Load 1-Click Demo Spec
        </button>
      </div>

      {demoLoaded && (
        <div className="mb-6 p-4 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-900 text-sm flex items-start space-x-3">
          <CheckCircle2 className="h-5 w-5 text-indigo-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Demo configuration loaded!</span>
            <p className="mt-1 text-xs text-indigo-700">
              Pre-filled with the Sample Target API (<code className="bg-indigo-100 px-1 py-0.5 rounded">http://localhost:8001</code>) and set to <strong>Mock Provider</strong> so anyone can test with <strong>zero API keys required</strong>. Click <em>Create Run</em> below to proceed!
            </p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">Target API URL</label>
          <input
            type="url"
            required
            value={targetUrl}
            onChange={e => setTargetUrl(e.target.value)} 
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          />
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">LLM Provider</label>
            <select
              value={provider}
              onChange={e => {
                const val = e.target.value;
                setProvider(val);
                if (val === 'gemini') setModel('gemini-3.6-flash');
                else if (val === 'openai') setModel('gpt-4o-mini');
                else if (val === 'mock') setModel('mock-standard');
              }}
              className="mt-1 block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            >
              <option value="gemini">Google Gemini (AI Generation)</option>
              <option value="mock">⚡ Mock / Demo Provider (Zero API Keys Needed)</option>
              <option value="openai">OpenAI</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Model</label>
            <input
              type="text"
              value={model}
              onChange={e => setModel(e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Number of Tests to Generate</label>
          <input
            type="number"
            min="1"
            max="50"
            value={testCount}
            onChange={e => setTestCount(parseInt(e.target.value))}
            className="mt-1 block w-32 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
          />
        </div>

        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="block text-sm font-medium text-gray-700">OpenAPI Specification (JSON or YAML)</label>
            <button
              type="button"
              onClick={loadDemoSpec}
              className="text-xs text-indigo-600 hover:text-indigo-800 underline"
            >
              Insert sample spec
            </button>
          </div>
          <textarea
            required
            rows={10}
            value={apiSpec}
            onChange={e => setApiSpec(e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 font-mono text-xs focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Paste your OpenAPI 3.0 spec here, or click 'Load 1-Click Demo Spec' above..."
          />
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
          <button
            type="button"
            onClick={loadDemoSpec}
            className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
          >
            Reset to Demo
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex justify-center py-2 px-5 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Creating Run...' : 'Create Run'}
          </button>
        </div>
      </form>
    </div>
  );
}
