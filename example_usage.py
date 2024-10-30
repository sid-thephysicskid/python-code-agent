from manim import *
from code_agent.manim_agent import ManimAgent

agent = ManimAgent()

# prompt = """Create a manim animation that shows a circle morphing into a square, 
#            while displaying the equation for the area of each shape during the transformation."""

prompt = "Create a Manim animation that shows how a 2x2 matrix multiplcation is performed."

prompt2 = """Create a manim animation that demonstrates the chain rule for derivatives.
           Show d/dx[f(g(x))] = f'(g(x)) * g'(x) using a concrete example like f(x)=x² and g(x)=sin(x).
           Use color coding to track each function's contribution."""


prompt3 = """Create a manim animation demonstrating Gaussian elimination on a 3x3 matrix.
           Show each step of the process, with:
           1. Highlighting of the current pivot element
           2. Animated row operations with equations
           3. Tracking of determinant changes
           4. Final solution visualization"""
prompt4 = """Show how voltage, current, and resistance relate in a circuit using Ohm's Law (V=IR)"""

try:
    result = agent.solve(prompt)
    print(f"\nAnimation created successfully in {result['iterations']} iterations!")
    print("\nFinal Manim code:")
    print(result["implementation"])
    print(f"\nScene class name: {result['scene_class']}")
    print("\nAnimation has been rendered!")
except Exception as e:
    print(f"Failed to create animation: {str(e)}")
