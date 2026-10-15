# Frontend Deep Dive

The frontend is a modern, responsive Single Page Application (SPA) designed to provide clear visibility into complex AI testing pipelines.

## 1. Technology Stack
- **Framework**: React 19 bootstrapped with Vite for instant server start and fast HMR (Hot Module Replacement).
- **Styling**: TailwindCSS 4 provides utility-first styling, enabling rapid UI development directly within JSX without context-switching to CSS files.
- **Routing**: `react-router-dom` handles client-side routing, keeping the UI state synchronized with the URL.
- **Icons**: `lucide-react` is used for clean, modern iconography.

## 2. Core Views

### `App.tsx` (Shell & Routing)
- Serves as the application shell, containing the persistent top navigation bar and layout wrappers.
- Defines the main route structure:
  - `/`: Dashboard
  - `/runs/new`: Run Creator
  - `/runs/:runId`: Run Details

### `Dashboard.tsx`
- **Purpose**: Provides a high-level overview of testing health across all historical runs.
- **Mechanics**: Fetches aggregate data from the backend. Likely features summary metrics (total tests run, average pass rate) and a list of recent test runs with quick links to their details.

### `RunCreator.tsx`
- **Purpose**: The configuration entry point.
- **Mechanics**: A controlled form component where users configure the run. They input the target API base URL, paste the OpenAPI specification (JSON/YAML), and select the AI provider configuration. On submission, it POSTs to the backend and redirects the user to the newly created Run Details view.

### `RunDetails.tsx`
- **Purpose**: The most complex view in the application. It visualizes the state machine of a test run.
- **Mechanics**: 
  - Tracks the run status (`pending` -> `generating` -> `executing` -> `completed`).
  - Displays quantitative metrics: tests generated, valid vs. invalid tests, pass/fail counts.
  - Lists individual test cases. It allows users to expand a test case to see the exact AI generation logic (expected outcomes) alongside the actual HTTP execution result (actual response body, headers, and status code).
  - Handles the action buttons for triggering the "Generate Tests" and "Execute Run" API calls.

## 3. Design Principles
- **Separation of Concerns**: UI components handle display logic, while Axios (or `fetch`) is used to abstract network calls to the FastAPI backend.
- **Feedback Loops**: Given the asynchronous nature of LLM generation and HTTP execution, the UI focuses on providing clear loading states, error boundaries, and status indicators so the user is never left wondering what the system is doing.
