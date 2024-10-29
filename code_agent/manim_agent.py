from anthropic import Anthropic
from manim import *
import pytest
import tempfile
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .config import Config
from .exceptions import MaxIterationsReached, TestGenerationError
from .test_result import TestResult

class ManimAgent(Scene):
    def __init__(self, anthropic_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__()
        self.client = Anthropic(api_key=anthropic_key or Config.ANTHROPIC_API_KEY)
        self.model = model or Config.MODEL
        self.max_iterations = Config.MAX_ITERATIONS
        self.attempt_history = []
        self.test_results_history = []
        self.current_iteration = 0

    def _build_implementation_context(self) -> str:
        """Build context from previous implementation attempts."""
        if not self.attempt_history:
            return "This is the first attempt."
            
        context = "Previous attempts and their results:\n\n"
        for i, (attempt, result) in enumerate(zip(self.attempt_history, self.test_results_history)):
            context += f"Attempt {i+1}:\n"
            context += f"Implementation:\n{attempt}\n"
            context += f"Test Results:\n{result.output}\n"
            if result.manim_specific_errors:
                context += f"Manim Errors:\n{', '.join(result.manim_specific_errors)}\n"
            context += "---\n"
        
        return context

    def generate_test(self, prompt: str) -> str:
        """Generate Manim-specific test code."""
        system_prompt = """You are an expert Manim developer creating pytest tests.
        Create precise tests that verify:
        1. Scene initialization and structure
        2. Correct creation of geometric objects (Circle, Square)
        3. Proper mathematical text rendering using MathTex for area equations
        4. Animation sequence and transformations
        5. Final state of the scene
        
        DO NOT add unnecessary constraints like equal areas between shapes unless specifically requested."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Write pytest tests for this Manim animation: {prompt}"
                }]
            )
            
            test_code = response.content[0].text
            # Clean up any markdown formatting
            if "```python" in test_code:
                test_code = test_code.split("```python")[1].split("```")[0]
            elif "```" in test_code:
                test_code = test_code.split("```")[1]
                
            return test_code.strip()
            
        except Exception as e:
            raise TestGenerationError(f"Failed to generate tests: {str(e)}")

    def generate_implementation(self, prompt: str, test_code: str) -> str:
        """Generate Manim implementation code."""
        context = self._build_implementation_context()
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system="""You are an expert Manim developer.
                Create a precise, working implementation following these guidelines:
                1. Use proper Manim syntax and conventions
                2. Create smooth animations with appropriate timing
                3. Position objects carefully using next_to() or move_to()
                4. Use MathTex for mathematical formulas with proper escaping
                5. Handle transformations properly with self.play()
                6. Consider the viewing window and object scales
                7. Ensure all f-strings are properly formatted
                8. Use raw strings (r) for LaTeX expressions
                
                Example of correct MathTex and f-string usage:
                final_det_text = MathTex(r"\\text{Final det} = " + f"{final_det:.2f}")
                """,
                messages=[{
                    "role": "user",
                    "content": f"""Create a Manim implementation for: {prompt}

Previous attempts context:
{context}

The test code is:
{test_code}

Important: Ensure proper f-string syntax and LaTeX escaping in all text elements."""
                }]
            )
            
            implementation = response.content[0].text
            if "```python" in implementation:
                implementation = implementation.split("```python")[1].split("```")[0]
            elif "```" in implementation:
                implementation = implementation.split("```")[1]
                
            return implementation.strip()
            
        except Exception as e:
            raise TestGenerationError(f"Failed to generate implementation: {str(e)}")

    def run_tests(self, test_code: str, implementation_code: str) -> TestResult:
        """Run tests with Manim-specific error catching."""
        start_time = datetime.now()
        failed_tests = []
        manim_errors = []
        
        # Pre-check implementation for common syntax errors
        try:
            compile(implementation_code, '<string>', 'exec')
        except SyntaxError as e:
            return TestResult(
                passed=False,
                output=f"Syntax error in implementation: {str(e)}",
                failed_tests=["syntax_check"],
                execution_time=0,
                manim_specific_errors=[str(e)]
            )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as impl_file:
            try:
                full_implementation = "from manim import *\nimport numpy as np\n" + implementation_code
                impl_file.write(full_implementation)
                impl_path = impl_file.name
            except Exception as e:
                return TestResult(
                    passed=False,
                    output=f"Failed to write implementation: {str(e)}",
                    failed_tests=["file_write"],
                    execution_time=0,
                    manim_specific_errors=[str(e)]
                )

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as test_file:
            full_test = f"""
import pytest
from manim import *
from {os.path.splitext(os.path.basename(impl_path))[0]} import *

{test_code}
"""
            test_file.write(full_test)
            test_path = test_file.name

        try:
            class ManimTestPlugin:
                def pytest_runtest_logreport(self, report):
                    if report.failed:
                        failed_tests.append({
                            'name': report.nodeid,
                            'error': report.longrepr,
                            'phase': report.when
                        })
                        if any(keyword in str(report.longrepr) for keyword in 
                              ['VMobject', 'Camera', 'Scene', 'Animation', 'Transform']):
                            manim_errors.append(str(report.longrepr))

            plugin = ManimTestPlugin()
            result = pytest.main(["-v", test_path], plugins=[plugin])
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return TestResult(
                passed=len(failed_tests) == 0,
                output=str(failed_tests),
                failed_tests=[f['name'] for f in failed_tests],
                execution_time=execution_time,
                manim_specific_errors=manim_errors
            )
        finally:
            os.unlink(impl_path)
            os.unlink(test_path)

    def solve(self, prompt: str) -> Dict[str, str]:
        """Main method to generate and test Manim animations."""
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
                scene_class_name = self._extract_scene_class_name(implementation)
                self._render_animation(implementation, scene_class_name)
                return {
                    "test_code": test_code,
                    "implementation": implementation,
                    "iterations": self.current_iteration + 1,
                    "scene_class": scene_class_name
                }
            else:
                print("\nTests failed. Analyzing failures...")
                analysis = self._analyze_test_failure(test_result)
                print(f"Analysis: {analysis}")
                print("Generating new implementation...")
            
            self.current_iteration += 1
        
        raise MaxIterationsReached("Failed to generate passing implementation within max iterations")

    def _extract_scene_class_name(self, implementation: str) -> str:
        """Extract the main scene class name from the implementation."""
        import ast
        tree = ast.parse(implementation)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and 'Scene' in [base.id for base in node.bases]:
                return node.name
        return "MainScene"  # Default name if not found

    def _analyze_test_failure(self, test_result: TestResult) -> str:
        """Analyze Manim-specific test failures."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system="You are a Manim expert. Analyze these test failures and provide specific guidance for fixing Manim animations.",
                messages=[{
                    "role": "user",
                    "content": f"""
Analyze these Manim test failures:

Test Output:
{test_result.output}

Manim-specific Errors:
{test_result.manim_specific_errors}

Provide specific guidance on:
1. Animation sequence issues
2. Object transformation problems
3. Mathematical accuracy issues
4. Scene composition problems
                    """
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Failed to analyze test failures: {str(e)}"

    def _render_animation(self, implementation: str, scene_class_name: str) -> None:
        """Render the Manim animation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(f"from manim import *\n{implementation}")
            temp_path = f.name

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("manim_module", temp_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            with tempconfig({
                "quality": Config.MANIM_QUALITY,
                "preview": Config.MANIM_PREVIEW,
                "format": Config.MANIM_FORMAT,
                # "pixel_width": Config.MANIM_WIDTH,
                # "pixel_height": Config.MANIM_HEIGHT,
                # "frame_rate": Config.MANIM_FPS,
            }):
                scene_class = getattr(module, scene_class_name)
                scene = scene_class()
                scene.render()
        finally:
            os.unlink(temp_path)

    def _validate_implementation(self, implementation_code: str) -> List[str]:
        """Validate implementation for common Manim issues."""
        errors = []
        
        # Check for proper MathTex usage
        if "\\text{" in implementation_code and not "r\"" in implementation_code:
            errors.append("LaTeX text commands should use raw strings (r)")
            
        # Check for f-string syntax in MathTex
        if "f\"\\text" in implementation_code:
            errors.append("Avoid f-strings directly in LaTeX expressions")
            
        # Check for proper animation sequencing
        if "self.play(" in implementation_code and "self.wait()" not in implementation_code:
            errors.append("Animations should include wait() calls for proper timing")
            
        return errors
