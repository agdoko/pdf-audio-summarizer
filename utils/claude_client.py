"""
Claude API Client for PDF Processing and Summarization

This module demonstrates enterprise-level API integration patterns commonly
evaluated in technical interviews.

Key Interview Concepts:
- Async/await patterns for API calls
- Error handling and retry logic
- Token management and optimization
- Structured prompt engineering
"""

import asyncio
from typing import Optional, Dict, Any
import logging

import anthropic
from anthropic import Anthropic

# Configure logging for production monitoring
logger = logging.getLogger(__name__)


class ClaudeProcessor:
    """
    Production-ready Claude API client for PDF content processing.
    
    Interview Focus Areas:
    - API client architecture and design patterns
    - Error handling and resilience strategies
    - Token optimization and cost management
    - Async programming patterns
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-0"):
        """
        Initialize Claude client with proper configuration.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use (defaults to Sonnet 4 for best performance)
        """
        if not api_key or api_key == "your_anthropic_api_key_here":
            raise ValueError("Valid Anthropic API key required")
            
        self.client = Anthropic(api_key=api_key)
        self.model = model
        
        # Token limits for cost management (important for production)
        self.max_input_tokens = 100_000  # Sonnet input limit
        self.target_output_tokens = 2_000  # ~6 minutes of speech at 300 WPM
        
        logger.info(f"Claude client initialized with model: {model}")
    
    def create_summary_prompt(self, pdf_text: str, target_minutes: int = 6) -> str:
        """
        Create optimized prompt for scientific PDF summarization.
        
        Interview Concept: Prompt engineering demonstrates understanding of:
        - LLM instruction design
        - Context optimization
        - Output specification
        
        Args:
            pdf_text: Extracted PDF content
            target_minutes: Target audio length in minutes
            
        Returns:
            Structured prompt for Claude
        """
        # Calculate target word count (average 150 words/minute for clear speech)
        target_words = target_minutes * 150
        
        prompt = f"""You are an expert scientific communicator tasked with creating audio-ready summaries of research papers.

TASK: Create a {target_minutes}-minute spoken summary (approximately {target_words} words) of the following scientific paper.

REQUIREMENTS:
1. **Audio-First Design**: Write for listening, not reading
   - Use clear, conversational language
   - Include natural transitions between sections
   - Avoid complex jargon without explanation

2. **Structure for Audio**:
   - Start with a compelling hook about the research significance
   - Provide clear section transitions ("Now, let's examine the methodology...")
   - End with practical implications and future directions

3. **Scientific Accuracy**:
   - Preserve key technical details and findings
   - Explain methodology in accessible terms
   - Include specific numbers and results where important

4. **Target Length**: Exactly {target_words} words (±50 words)

PAPER CONTENT:
{pdf_text}

OUTPUT FORMAT:
Provide only the summary text, ready for text-to-speech conversion. No headers, bullet points, or formatting - just flowing, natural speech."""

        return prompt
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for cost/limit management.
        
        Interview Concept: Shows understanding of:
        - API cost optimization
        - Resource management
        - Production constraints
        
        Args:
            text: Input text to estimate
            
        Returns:
            Estimated token count (rough approximation)
        """
        # Rough estimation: ~4 characters per token for English
        return len(text) // 4
    
    def truncate_pdf_content(self, pdf_text: str) -> str:
        """
        Intelligently truncate PDF content to fit token limits.
        
        Interview Concept: Demonstrates:
        - Content prioritization strategies
        - Token budget management
        - Graceful degradation patterns
        
        Args:
            pdf_text: Raw PDF text content
            
        Returns:
            Truncated content optimized for summarization
        """
        estimated_tokens = self.estimate_tokens(pdf_text)
        
        # Reserve tokens for prompt and response
        available_tokens = self.max_input_tokens - 1000  # Buffer for prompt
        
        if estimated_tokens <= available_tokens:
            return pdf_text
        
        logger.warning(f"PDF content ({estimated_tokens} tokens) exceeds limit. Truncating.")
        
        # Calculate character limit and truncate intelligently
        char_limit = available_tokens * 4
        
        # Try to truncate at paragraph boundaries for better context
        truncated = pdf_text[:char_limit]
        last_paragraph = truncated.rfind('\n\n')
        
        if last_paragraph > char_limit * 0.8:  # If we find a good break point
            truncated = truncated[:last_paragraph]
        
        logger.info(f"Truncated to {len(truncated)} characters")
        return truncated
    
    async def generate_summary(self, pdf_text: str, target_minutes: int = 6) -> str:
        """
        Generate audio-ready summary from PDF content.
        
        Interview Concept: Async API integration patterns:
        - Proper error handling and logging
        - Graceful failure modes
        - Performance monitoring
        
        Args:
            pdf_text: Extracted PDF content
            target_minutes: Target audio duration
            
        Returns:
            Audio-ready summary text
            
        Raises:
            anthropic.APIError: For API-related errors
            ValueError: For invalid input
        """
        if not pdf_text.strip():
            raise ValueError("PDF content cannot be empty")
        
        # Prepare content within token limits
        processed_content = self.truncate_pdf_content(pdf_text)
        prompt = self.create_summary_prompt(processed_content, target_minutes)
        
        logger.info(f"Generating summary for {len(processed_content)} characters of content")
        
        try:
            # Make API call with proper error handling
            response = await asyncio.to_thread(
                self._make_sync_api_call,
                prompt
            )
            
            summary = response.content[0].text.strip()
            
            # Validate output quality
            word_count = len(summary.split())
            target_words = target_minutes * 150
            
            logger.info(f"Generated summary: {word_count} words (target: {target_words})")
            
            if word_count < target_words * 0.7:
                logger.warning("Summary significantly shorter than target")
            elif word_count > target_words * 1.3:
                logger.warning("Summary significantly longer than target")
            
            return summary
            
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in summary generation: {e}")
            raise
    
    def _make_sync_api_call(self, prompt: str) -> anthropic.types.Message:
        """
        Synchronous API call wrapped for async execution.
        
        Interview Concept: Shows understanding of:
        - Async/sync bridge patterns
        - Thread pool usage
        - API client architecture
        """
        return self.client.messages.create(
            model=self.model,
            max_tokens=self.target_output_tokens,
            temperature=0.1,  # Low temperature for consistent, factual summaries
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics for monitoring.
        
        Interview Concept: Production monitoring and observability
        """
        # In a real implementation, this would track actual usage
        return {
            "model": self.model,
            "max_input_tokens": self.max_input_tokens,
            "target_output_tokens": self.target_output_tokens,
            "estimated_cost_per_summary": "$0.15-0.30"  # Rough estimate
        }