from code_agent.agent import CodeAgent
from code_agent.config import Config

Config.validate()


agent = CodeAgent()

prompt = "Write a function that calculates the factorial of a given number."

# Solve the problem
try:
    result = agent.solve(prompt)
    print("\nFinal Result:")
    print("Test Code:")
    print(result["test_code"])
    print("\nImplementation:")
    print(result["implementation"])
    print(f"\nSolved in {result['iterations']} iterations.")
except Exception as e:
    print(f"An error occurred: {str(e)}")