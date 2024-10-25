import openai
import pytest
import tempfile
import os
from typing import Dict, List, Optional, Tuple
from .config import Config
from .exceptions import MaxIterationsReached, TestGenerationError

class CodeAgent:
    def __init__(self, openai_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize CodeAgent with OpenAI credentials."""
        self.client = openai.OpenAI(api_key=openai_key or Config.OPENAI_API_KEY)
        self.model = model or Config.MODEL
        self.max_iterations = Config.MAX_ITERATIONS
        
    def generate_test(self, prompt: str) -> str:
        """Generate test code based on the prompt."""
        system_prompt = """You are an AI assistant that generates unit tests.
        1. Think step by step about what needs to be tested
        2. Generate comprehensive pytest test cases
        3. Start with basic cases and progress to edge cases
        4. Keep tests focused and isolated"""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Write pytest tests for: {prompt}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise TestGenerationError(f"Failed to generate tests: {str(e)}")

    def generate_implementation(self, prompt: str, test_code: str, error_message: Optional[str] = None) -> str:
        """Generate implementation code based on prompt and test."""
        system_prompt = """You are an AI assistant that implements code to pass unit tests.
        1. Think step by step about the solution
        2. Consider edge cases
        3. Write clean, maintainable code
        4. Fix any test failures mentioned"""
        
        user_prompt = f"""
        Implement code to satisfy this prompt: {prompt}
        
        The test code is:
        {test_code}
        
        {f'Previous error: {error_message}' if error_message else ''}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        
        return response.choices[0].message.content

    def run_tests(self, test_code: str, implementation_code: str) -> Tuple[bool, str]:
        """Run the tests against the implementation."""
        # Create temporary files for test and implementation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as impl_file:
            impl_file.write(implementation_code)
            impl_path = impl_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as test_file:
            # Modify test code to import from implementation file
            modified_test = f"from {os.path.splitext(os.path.basename(impl_path))[0]} import *\n\n{test_code}"
            test_file.write(modified_test)
            test_path = test_file.name

        try:
            # Run pytest programmatically
            pytest.main(["-v", test_path])
            return True, ""
        except Exception as e:
            return False, str(e)
        finally:
            # Cleanup temporary files
            os.unlink(impl_path)
            os.unlink(test_path)

    def solve(self, prompt: str) -> Dict[str, str]:
        """Main method to generate tests and implementation until tests pass."""
        print(f"Generating tests for prompt: {prompt}")
        test_code = self.generate_test(prompt)
        print("\nGenerated test code:")
        print(test_code)
        
        for i in range(self.max_iterations):
            print(f"\nIteration {i+1}/{self.max_iterations}")
            implementation = self.generate_implementation(prompt, test_code)
            print("\nGenerated implementation:")
            print(implementation)
            
            success, error = self.run_tests(test_code, implementation)
            if success:
                print("\nAll tests passed!")
                return {
                    "test_code": test_code,
                    "implementation": implementation,
                    "iterations": i+1
                }
            else:
                print(f"\nTests failed. Error: {error}")
                print("Generating new implementation...")
        
        raise Exception("Failed to generate passing implementation within max iterations")
