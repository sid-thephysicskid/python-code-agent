import streamlit as st
from code_agent.manim_agent import ManimAgent
from code_agent.config import Config
import tempfile
import os
import shutil
from pathlib import Path

st.set_page_config(
    page_title="Math Concept Animator",
    page_icon="🎬",
    layout="wide"
)

def get_latest_video() -> str:
    """Get the path of the latest generated video."""
    video_dir = Path("media/videos/720p30")  # Manim's default output directory
    if not video_dir.exists():
        return None
        
    video_files = list(video_dir.glob("*.mp4"))
    if not video_files:
        return None
        
    return str(max(video_files, key=os.path.getctime))

def create_animation(prompt: str) -> tuple[str, str]:
    """Create animation and return the video path and implementation code."""
    agent = ManimAgent()
    
    with st.spinner('Generating animation... This might take a minute...'):
        try:
            result = agent.solve(prompt)
            video_path = get_latest_video()
            
            if video_path and os.path.exists(video_path):
                # Read the video file as bytes
                with open(video_path, 'rb') as f:
                    video_bytes = f.read()
                return video_bytes, result["implementation"]
            else:
                st.error("Video file not found after generation")
                return None, result["implementation"]
            
        except Exception as e:
            st.error(f"Failed to create animation: {str(e)}")
            return None, None

def main():
    st.title("🎬 Math Concept Animator")
    st.subheader("Turn mathematical concepts into animations!")

    # Example prompts
    st.sidebar.header("Example Prompts")
    example_prompts = {
        "Matrix Multiplication": "Create a Manim animation that shows how a 2x2 matrix multiplication is performed.",
        "Chain Rule": """Create a manim animation that demonstrates the chain rule for derivatives.
                     Show d/dx[f(g(x))] = f'(g(x)) * g'(x) using f(x)=x² and g(x)=sin(x).""",
        "Gaussian Elimination": """Create a manim animation demonstrating Gaussian elimination on a 3x3 matrix.
                               Show each step with highlighting and row operations."""
    }
    
    for title, prompt in example_prompts.items():
        if st.sidebar.button(title):
            st.session_state.prompt = prompt

    # Main input area
    prompt = st.text_area(
        "Describe the mathematical concept you want to animate:",
        value=st.session_state.get("prompt", ""),
        height=100,
        help="Be specific about what you want to see in the animation."
    )

    # Quality settings
    st.sidebar.header("Animation Settings")
    quality = st.sidebar.selectbox(
        "Quality",
        ["low_quality", "medium_quality", "high_quality", "production_quality"],
        index=1
    )
    
    Config.MANIM_QUALITY = quality

    if st.button("Generate Animation", type="primary"):
        if not prompt:
            st.warning("Please enter a prompt first!")
            return
            
        video_bytes, implementation = create_animation(prompt)
        
        if video_bytes:
            # Display the animation using st.video with bytes
            st.success("Animation created successfully!")
            st.video(video_bytes)
            
            # Add download button
            st.download_button(
                label="Download Animation",
                data=video_bytes,
                file_name="math_animation.mp4",
                mime="video/mp4"
            )
            
            # Show the implementation code
            with st.expander("View Generated Code"):
                st.code(implementation, language="python")

    st.markdown("""
    ### Tips for better results:
    1. Be specific about what mathematical concept you want to visualize
    2. Mention any specific colors or visual elements you want
    3. Specify if you want step-by-step explanations
    4. Include any equations or formulas that should be shown
    """)

if __name__ == "__main__":
    main()
