"""
PDF Audio Summarizer - Streamlit Application

A production-ready web application that converts scientific PDFs into audio summaries
using Claude API for summarization and ElevenLabs for text-to-speech conversion.

This application demonstrates enterprise-level patterns commonly evaluated in
technical interviews for full-stack and AI engineering roles.

Key Technical Concepts Showcased:
- Async/await patterns in Streamlit
- API integration and error handling
- File processing and memory management
- User experience design for AI applications
- Production deployment configuration
"""

import asyncio
import logging
import os
from typing import Optional
import io

import streamlit as st
from dotenv import load_dotenv
import pdfplumber
import PyPDF2

from utils.claude_client import ClaudeProcessor
from utils.elevenlabs_client import ElevenLabsProcessor

# Configure logging for production monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class PDFAudioSummarizerApp:
    """
    Main application class encapsulating the PDF-to-audio pipeline.
    
    Interview Focus: Demonstrates object-oriented design, separation of concerns,
    and production-ready error handling patterns.
    """
    
    def __init__(self):
        """Initialize the application with API clients."""
        self.claude_client: Optional[ClaudeProcessor] = None
        self.elevenlabs_client: Optional[ElevenLabsProcessor] = None
        self.setup_page_config()
        self.initialize_clients()
    
    def setup_page_config(self) -> None:
        """Configure Streamlit page settings for professional appearance."""
        st.set_page_config(
            page_title="PDF Audio Summarizer",
            page_icon="🎧",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_clients(self) -> bool:
        """
        Initialize API clients with proper error handling.
        
        Returns:
            True if both clients initialized successfully
        """
        try:
            # Get API keys from environment
            claude_key = os.getenv("ANTHROPIC_API_KEY")
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            
            if not claude_key or claude_key == "your_anthropic_api_key_here":
                st.error("❌ Claude API key not configured. Please check your .env file.")
                return False
            
            if not elevenlabs_key or elevenlabs_key == "your_elevenlabs_api_key_here":
                st.error("❌ ElevenLabs API key not configured. Please check your .env file.")
                return False
            
            # Initialize clients
            self.claude_client = ClaudeProcessor(claude_key)
            self.elevenlabs_client = ElevenLabsProcessor(
                elevenlabs_key,
                voice_id=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
            )
            
            logger.info("API clients initialized successfully")
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to initialize API clients: {str(e)}")
            logger.error(f"Client initialization error: {e}")
            return False
    
    def extract_pdf_text(self, uploaded_file) -> Optional[str]:
        """
        Extract text from uploaded PDF with multiple fallback methods.
        
        Interview Concept: Robust file processing with graceful degradation
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Extracted text or None if extraction fails
        """
        if uploaded_file is None:
            return None
        
        try:
            # Method 1: Try pdfplumber (better for complex layouts)
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                
                if text.strip():
                    logger.info(f"Extracted {len(text)} characters using pdfplumber")
                    return text.strip()
        
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
        
        try:
            # Method 2: Fallback to PyPDF2
            uploaded_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            if text.strip():
                logger.info(f"Extracted {len(text)} characters using PyPDF2")
                return text.strip()
        
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}")
        
        # If all methods fail
        st.error("❌ Failed to extract text from PDF. Please ensure it's a text-based PDF.")
        return None
    
    def render_sidebar(self) -> dict:
        """
        Render configuration sidebar.
        
        Returns:
            Dictionary of user configuration options
        """
        st.sidebar.title("⚙️ Configuration")
        
        # Fixed summary length for optimal quality
        target_minutes = 3  # Fixed to 3 minutes for best results
        st.sidebar.info(f"🎧 Audio Length: {target_minutes} minutes (optimized)")
        
        # File size limit
        max_size_mb = int(os.getenv("MAX_PDF_SIZE_MB", "10"))
        st.sidebar.info(f"📄 Max PDF size: {max_size_mb}MB")
        
        # API status indicators
        st.sidebar.title("🔧 System Status")
        
        if self.claude_client:
            st.sidebar.success("✅ Claude API: Connected")
        else:
            st.sidebar.error("❌ Claude API: Not configured")
        
        if self.elevenlabs_client:
            st.sidebar.success("✅ ElevenLabs: Connected")
        else:
            st.sidebar.error("❌ ElevenLabs: Not configured")
        
        # Usage information
        with st.sidebar.expander("💡 Usage Tips"):
            st.write("""
            **Best Results:**
            - Upload text-based PDFs (not scanned images)
            - Scientific papers work best
            - Clear, well-formatted documents
            
            **Processing Time:**
            - Text extraction: ~5 seconds
            - Summary generation: ~30-60 seconds  
            - Audio generation: ~30-45 seconds
            
            **Audio Quality:**
            - 3-minute summaries optimized for clarity
            - Professional narration with cloned voice
            - High-quality MP3 output (44.1kHz)
            """)
        
        return {
            "target_minutes": target_minutes,
            "max_size_mb": max_size_mb
        }
    
    def render_main_interface(self, config: dict) -> None:
        """Render the main application interface."""
        st.title("🎧 PDF Audio Summarizer")
        st.markdown("""
        Transform scientific PDFs into engaging 3-minute audio summaries using AI.
        Upload a research paper and get a professional narrated summary optimized for clarity.
        """)
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Choose a PDF file",
            type="pdf",
            help=f"Upload a PDF file (max {config['max_size_mb']}MB)"
        )
        
        if uploaded_file is not None:
            # Validate file size
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            
            if file_size_mb > config['max_size_mb']:
                st.error(f"❌ File too large ({file_size_mb:.1f}MB). Maximum size: {config['max_size_mb']}MB")
                return
            
            # Display file info
            st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size_mb:.1f}MB)")
            
            # Process button
            if st.button("🚀 Generate Audio Summary", type="primary"):
                if not self.claude_client or not self.elevenlabs_client:
                    st.error("❌ API clients not properly configured. Please check your .env file.")
                    return
                
                # Run the processing pipeline
                asyncio.run(self.process_pdf_to_audio(uploaded_file, config))
    
    async def process_pdf_to_audio(self, uploaded_file, config: dict) -> None:
        """
        Main processing pipeline: PDF → Text → Summary → Audio
        
        Interview Concept: Demonstrates async pipeline design, progress tracking,
        and comprehensive error handling.
        """
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Extract text from PDF
            status_text.text("📄 Extracting text from PDF...")
            progress_bar.progress(20)
            
            pdf_text = self.extract_pdf_text(uploaded_file)
            if not pdf_text:
                st.error("❌ Failed to extract text from PDF")
                return
            
            # Display extraction stats
            word_count = len(pdf_text.split())
            st.info(f"📊 Extracted {word_count:,} words from PDF")
            
            # Step 2: Generate summary with Claude
            status_text.text("🤖 Generating summary with Claude AI...")
            progress_bar.progress(40)
            
            summary = await self.claude_client.generate_summary(
                pdf_text, 
                target_minutes=config['target_minutes']
            )
            
            # Display summary preview
            summary_words = len(summary.split())
            st.success(f"✅ Summary generated ({summary_words} words)")
            
            with st.expander("📝 Preview Summary"):
                st.write(summary)
            
            # Step 3: Generate audio with ElevenLabs
            status_text.text("🎵 Converting to audio with ElevenLabs...")
            progress_bar.progress(70)
            
            audio_file = await self.elevenlabs_client.text_to_audio_file(
                summary,
                filename=f"{uploaded_file.name.replace('.pdf', '')}_summary.mp3"
            )
            
            # Step 4: Provide download
            status_text.text("✅ Processing complete!")
            progress_bar.progress(100)
            
            # Audio player and download
            st.success("🎉 Audio summary ready!")
            
            # Play audio
            st.audio(audio_file, format="audio/mp3")
            
            # Download button
            st.download_button(
                label="⬇️ Download MP3",
                data=audio_file,
                file_name=audio_file.name,
                mime="audio/mp3"
            )
            
            # Processing stats
            estimated_duration = self.elevenlabs_client.estimate_audio_duration(summary)
            st.info(f"🎧 Audio duration: ~{estimated_duration:.1f} minutes")
            
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
            logger.error(f"Processing pipeline error: {e}")
            
        finally:
            # Clean up progress indicators
            progress_bar.empty()
            status_text.empty()
    
    def render_footer(self) -> None:
        """Render application footer with technical information."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔧 Technical Stack**")
            st.markdown("""
            - **Frontend**: Streamlit
            - **AI**: Claude 3 Sonnet  
            - **TTS**: ElevenLabs Rachel
            - **PDF**: pdfplumber + PyPDF2
            """)
        
        with col2:
            st.markdown("**⚡ Performance**")
            st.markdown("""
            - **Processing**: ~2-3 minutes total
            - **Audio Quality**: Professional grade
            - **Accuracy**: Scientific content optimized
            - **Cost**: ~$0.45-0.60 per summary
            """)
        
        with col3:
            st.markdown("**🚀 Deployment**")
            st.markdown("""
            - **Platform**: Streamlit Community Cloud
            - **Repository**: GitHub integration
            - **Environment**: Python 3.12+
            - **Dependencies**: uv package manager
            """)
    
    def run(self) -> None:
        """Main application entry point."""
        # Render sidebar configuration
        config = self.render_sidebar()
        
        # Render main interface
        self.render_main_interface(config)
        
        # Render footer
        self.render_footer()


# Application entry point
if __name__ == "__main__":
    app = PDFAudioSummarizerApp()
    app.run()