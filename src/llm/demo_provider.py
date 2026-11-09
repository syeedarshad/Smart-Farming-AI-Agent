"""
src/llm/demo_provider.py
Demo LLM provider — generates structured answers directly from retrieved knowledge chunks.
Does NOT call any external service.
ALWAYS clearly labels its responses as Demo Mode.
Does NOT pretend to be IBM Granite.
"""
import logging
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)

_DEMO_HEADER = (
    "**[DEMO MODE — Response generated from local knowledge base, "
    "not by IBM Granite or any external AI model]**\n\n"
)

_DEMO_FOOTER = (
    "\n\n---\n"
    "*This response is based on retrieved agricultural knowledge. "
    "For district-specific advice, always consult your local KVK or agricultural officer. "
    "IBM Granite integration will provide enhanced multilingual answers when configured.*"
)


class DemoProvider(LLMProvider):
    """
    Demo provider that structures an answer from retrieved context chunks.
    Suitable for testing the application without any API credentials.
    """

    @property
    def provider_name(self) -> str:
        return "Demo (Local Knowledge Base)"

    @property
    def is_demo(self) -> bool:
        return True

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Parse the prompt to extract context and question, then
        assemble a structured, honest answer.
        """
        try:
            return _DEMO_HEADER + self._build_answer(prompt) + _DEMO_FOOTER
        except Exception as exc:
            logger.error("DemoProvider.generate error: %s", exc)
            return (
                _DEMO_HEADER
                + "I was unable to process this query. Please try rephrasing your question."
                + _DEMO_FOOTER
            )

    def _build_answer(self, prompt: str) -> str:
        """
        Extract the context section from the prompt and present it
        as a structured answer.
        """
        # Split the prompt at standard markers
        context_section = ""
        question_section = ""

        if "--- RETRIEVED KNOWLEDGE ---" in prompt and "--- FARMER'S QUESTION ---" in prompt:
            parts = prompt.split("--- RETRIEVED KNOWLEDGE ---")
            if len(parts) > 1:
                remainder = parts[1]
                context_parts = remainder.split("--- FARMER'S QUESTION ---")
                context_section = context_parts[0].strip()
                if len(context_parts) > 1:
                    question_section = context_parts[1].strip()
                    # Strip language instruction if present
                    if "--- LANGUAGE INSTRUCTION ---" in question_section:
                        question_section = question_section.split("--- LANGUAGE INSTRUCTION ---")[0].strip()
        else:
            # Fallback: use the whole prompt as context
            context_section = prompt

        if not context_section or context_section == "No relevant information found in the knowledge base.":
            return (
                "I don't have sufficient information in my knowledge base to answer "
                "this question confidently. Please consult your local KVK or agricultural officer."
            )

        # Build a readable answer from the retrieved context
        lines = [
            "Based on the agricultural knowledge base, here is the relevant information:\n",
        ]

        # Extract and clean the context
        context_lines = context_section.split("\n")
        useful_lines = []
        for line in context_lines:
            line = line.strip()
            if line and not line.startswith("Source:") and len(line) > 10:
                useful_lines.append(line)

        # Show up to ~30 meaningful lines
        for line in useful_lines[:35]:
            lines.append(line)

        if question_section:
            lines.append(f"\n**Your question:** {question_section}")

        lines.append(
            "\n**Note:** This is a summary from the knowledge base. "
            "Always verify with your local agricultural officer or KVK for your specific location and conditions."
        )

        return "\n".join(lines)

    def health_check(self) -> dict:
        return {
            "ok": True,
            "message": "Demo provider is active. No external API credentials are needed.",
        }
