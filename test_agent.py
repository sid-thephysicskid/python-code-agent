from code_agent.agent import CodeAgent
from code_agent.config import Config

Config.validate()


agent = CodeAgent()

prompt = "Create a function in Python that accepts one parameter: a string that’s a sentence. This function should return True if any word in that sentence contains duplicate letters and False if not."

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