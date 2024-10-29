from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MODEL = "claude-3-5-sonnet-latest"
    MAX_ITERATIONS = 10
    
    # Manim rendering settings
    MANIM_QUALITY = "medium_quality"  # low_quality, medium_quality, high_quality, production_quality
    MANIM_PREVIEW = True
    MANIM_FORMAT = "mp4"
    MANIM_WIDTH = 1920
    MANIM_HEIGHT = 1080
    MANIM_FPS = 60

    @classmethod
    def validate(cls):
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")