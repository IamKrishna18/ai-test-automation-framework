# 19. Mock Interview Instructions

To truly master this material, you must practice saying it out loud. Use this document to run mock interviews with a friend, a mentor, or even an AI voice assistant (like ChatGPT Voice).

## Setup
1. Provide the interviewer with a copy of your resume and the `18-interview-questions.md` file.
2. Set a timer for 45 minutes.
3. Treat it like a real interview: no looking at notes (unless absolutely stuck), dress appropriately (if doing video), and maintain a professional demeanor.

## Interview Structure (45 Minutes)

### Phase 1: Introduction (5-7 minutes)
*   **Interviewer:** "Tell me about yourself and your recent experience."
*   **You:** Give your standard introduction, leading into the AI Test Automation project as your crowning achievement.
*   **Interviewer:** "Can you give me a high-level overview of this AI Test Automation framework you built?"
*   **You:** Deliver your **60-Second Pitch**.

### Phase 2: Technical Deep Dive (20 minutes)
*   *Interviewer should pick 3-4 questions from the L2 and L3 section of the question bank.*
*   **Focus Area 1: Data Flow & Validation.** Be prepared to explain exactly how data moves from the OpenAPI spec upload to the LLM, and how it comes back and is validated. Draw it on a whiteboard or virtual notepad if possible.
*   **Focus Area 2: Async and Execution.** Explain how you handle executing tests without blocking the server.

### Phase 3: System Design & Scaling (10 minutes)
*   *Interviewer should ask an L4 question or a scaling question.*
*   **Scenario:** "We want to roll this out internally to our 50-person QA team. They will be uploading massive API specs and generating thousands of tests daily. Walk me through how you would scale your current architecture to support this."
*   *Your goal:* Discuss moving from SQLite to Postgres, putting the execution engine onto a task queue (Celery/Redis or AWS SQS), and handling rate limits from the LLM provider.

### Phase 4: Behavioral & Trade-offs (5 minutes)
*   **Interviewer:** "What was the hardest technical challenge you faced while building this, and how did you overcome it?"
*   **Interviewer:** "If you had two more weeks to work on this, what would you add or change?" (Reference `17-limitations.md`).

### Phase 5: Your Turn (3 minutes)
*   Have 2-3 questions prepared to ask the interviewer.

## Evaluation Criteria (For the Interviewer)
*   **Clarity:** Did the candidate explain complex AI/LLM concepts in a way that was easy to understand?
*   **Honesty:** Did the candidate admit to the limitations of their system, or did they pretend it was perfect?
*   **Depth:** When pushed on a technical choice (e.g., "Why not use MongoDB?"), did they have a solid, engineering-based justification?
*   **Delivery:** Did they speak confidently? Did they ramble, or keep answers concise and impactful?
