# Design Patterns & OOP (Phase 6, 20)

## Object-Oriented Programming (OOP)
The codebase heavily leverages OOP principles to keep the framework modular and extensible.
- **Encapsulation**: AI provider logic is encapsulated within specific classes so that API changes do not leak into the core business logic.
- **Polymorphism**: The system can switch between different AI models (e.g., GPT-4, Claude) because they all implement a common base interface.

## Design Patterns Used

### 1. Strategy Pattern
- **Where**: AI Model Selection and Test Execution strategies.
- **Why**: Allows the framework to swap out the underlying LLM provider dynamically at runtime based on configuration, without modifying the caller code.

### 2. Factory Method
- **Where**: Prompt Generation and Test Runner Instantiation.
- **Why**: Centralizes the creation logic. Depending on the language of the target code (Python, JS), the factory returns the appropriate language-specific test runner or prompt template.

### 3. Dependency Injection (DI)
- **Where**: FastAPI Routes and Services.
- **Why**: Database sessions, config settings, and AI service clients are injected into routes. This makes unit testing significantly easier since mock dependencies can be injected during tests.

### 4. Repository Pattern
- **Where**: Database access layer.
- **Why**: Abstracts the underlying database (SQLAlchemy) queries into a repository class, allowing the business logic to remain agnostic of the storage mechanism.
