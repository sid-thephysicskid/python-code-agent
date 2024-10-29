from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class TestResult:
    passed: bool
    output: str
    failed_tests: List[str]
    execution_time: float
    manim_specific_errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
