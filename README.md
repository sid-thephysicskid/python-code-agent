# Python Code Agent

A Python code-writing agent that generates both tests and implementation code using AI, ensuring the implementation passes all tests.

## Features

- Generates pytest test cases from natural language prompts
- Implements code that satisfies the generated tests
- Iterates until all tests pass or maximum iterations are reached

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sid-thephysicskid/python-code-agent.git
cd python-code-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the `.env.example` file to `.env` and set the environment variables.
```bash
cp .env.example .env
```
