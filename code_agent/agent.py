import openai
import pytest
import tempfile
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .config import Config
from .exceptions import MaxIterationsReached, TestGenerationError
from .test_result import TestResult

class CodeAgent:
    def __init__(self, openai_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize CodeAgent with OpenAI credentials and history tracking."""
        self.client = openai.OpenAI(api_key=openai_key or Config.OPENAI_API_KEY)
        self.model = model or Config.MODEL
        self.max_iterations = Config.MAX_ITERATIONS
        self.attempt_history = []
        self.test_results_history = []
        self.current_iteration = 0

    def _build_implementation_context(self) -> str:
        if not self.attempt_history:
            return "This is the first attempt."
            
        context = "Previous attempts and their results:\n\n"
        for i, (attempt, result) in enumerate(zip(self.attempt_history, self.test_results_history)):
            context += f"Attempt {i+1}:\n"
            context += f"Implementation:\n{attempt}\n"
            context += f"Test Results:\n{result.output}\n"
            context += f"Failed Tests: {', '.join(result.failed_tests)}\n"
            context += "---\n"
        
        return context

    def _analyze_test_failure(self, test_output: str) -> str:
        messages = [
            {"role": "system", "content": "You are a Python testing expert."},
            {"role": "user", "content": f"""
Analyze these test results and provide a concise explanation of why the tests failed:

{test_output}

Focus on:
1. Which specific tests failed
2. The expected vs actual behavior
3. Potential logical errors in the implementation
            """}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        
        return response.choices[0].message.content

    def generate_implementation(self, prompt: str, test_code: str, error_message: Optional[str] = None) -> str:
        context = self._build_implementation_context()
        
        system_prompt = """You are an AI assistant that implements code to pass unit tests.
        1. Think step by step about the solution
        2. Consider edge cases
        3. Write clean, maintainable code
        4. Fix any test failures mentioned"""
        
        user_prompt = f"""
        Implement code to satisfy this prompt: {prompt}
        
        The test code is:
        {test_code}
        
        Context from previous attempts:
        {context}
        
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

    def run_tests(self, test_code: str, implementation_code: str) -> TestResult:
        start_time = datetime.now()
        failed_tests = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as impl_file:
            impl_file.write(implementation_code)
            impl_path = impl_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as test_file:
            modified_test = f"from {os.path.splitext(os.path.basename(impl_path))[0]} import *\n\n{test_code}"
            test_file.write(modified_test)
            test_path = test_file.name

        try:
            import pytest
            pytest_output = []
            class PytestPlugin:
                def pytest_runtest_logreport(self, report):
                    if report.failed:
                        failed_tests.append(report.nodeid)
                    pytest_output.append(report)

            plugin = PytestPlugin()
            pytest.main(["-v", test_path], plugins=[plugin])
            
            execution_time = (datetime.now() - start_time).total_seconds()
            output = "\n".join(str(report) for report in pytest_output)
            
            return TestResult(
                passed=len(failed_tests) == 0,
                output=output,
                failed_tests=failed_tests,
                execution_time=execution_time
            )
        finally:
            os.unlink(impl_path)
            os.unlink(test_path)

    def solve(self, prompt: str) -> Dict[str, str]:
        print(f"Generating tests for prompt: {prompt}")
        test_code = self.generate_test(prompt)
        print("\nGenerated test code:")
        print(test_code)
        
        while self.current_iteration < self.max_iterations:
            print(f"\nIteration {self.current_iteration + 1}/{self.max_iterations}")
            
            implementation = self.generate_implementation(prompt, test_code)
            print("\nGenerated implementation:")
            print(implementation)
            
            test_result = self.run_tests(test_code, implementation)
            
            # Store attempt and results
            self.attempt_history.append(implementation)
            self.test_results_history.append(test_result)
            
            if test_result.passed:
                print("\nAll tests passed!")
                return {
                    "test_code": test_code,
                    "implementation": implementation,
                    "iterations": self.current_iteration + 1
                }
            else:
                print(f"\nTests failed. Error: {test_result.output}")
                print("Generating new implementation...")
            
            self.current_iteration += 1
        
        raise Exception("Failed to generate passing implementation within max iterations")
