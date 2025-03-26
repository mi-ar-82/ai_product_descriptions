# File: app/services/prompt_service.py
import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class PromptService:
    def __init__(self):
        # Create prompts directory if it doesn't exist
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.prompts_dir.mkdir(exist_ok = True)
        self.prompt_cache = {}
        print(f"Debug: Initializing prompt service with directory: {self.prompts_dir}")
        print(f"Debug: Type of prompts_dir: {type(self.prompts_dir)}")

    def get_prompt(self, prompt_name: str, api_type: str = "openai") -> Dict[str, Any]:
        """Load a prompt from JSON file."""
        cache_key = f"{api_type}_{prompt_name}"

        if cache_key in self.prompt_cache:
            return self.prompt_cache[cache_key]

        # Try to find specific API prompt first
        file_path = self.prompts_dir / f"{api_type}_{prompt_name}.json"
        if not file_path.exists():
            # Fall back to generic prompt
            file_path = self.prompts_dir / f"{prompt_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, "r", encoding = "utf-8") as f:
            prompt_data = json.load(f)

        print(f"Debug: Loaded prompt: {prompt_name} for API: {api_type}")
        print(f"Debug: Prompt data type: {type(prompt_data)}")

        self.prompt_cache[cache_key] = prompt_data
        return prompt_data

    def format_prompt_for_api(self, prompt_data: Dict[str, Any], product_info: Dict[str, Any],
                              api_type: str = "openai") -> List[Dict[str, Any]]:
        """Format a prompt for the specified API."""

        print(f"Debug: Formatting prompt for API: {api_type}")
        print(f"Debug: Product info type: {type(product_info)}")

        if api_type == "openai":
            content = [
                {"type": "text", "text": prompt_data["base_prompt"]},
                {"type": "text", "text": f"Product Title: {product_info['title']}"},
                {"type": "text", "text": f"Existing Description: {product_info['description']}"}
            ]

            # Add instructions
            for key, instruction in prompt_data["instructions"].items():
                content.append({"type": "text", "text": f"{key.upper()}: {instruction}"})

            # Add output format
            if "output_format" in prompt_data:
                content.append({"type": "text", "text": prompt_data["output_format"]})

            # Add image if available
            if product_info.get("image_url"):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": product_info["image_url"],
                        "detail": "low"
                    }
                })

            return [{"role": "user", "content": content}]

        elif api_type == "gemini":
            # Gemini-specific formatting for future implementation
            print("Debug: Gemini formatting not yet implemented")
            pass

        elif api_type == "perplexity":
            # Perplexity-specific formatting for future implementation
            print("Debug: Perplexity formatting not yet implemented")
            pass

        else:
            raise ValueError(f"Unsupported API type: {api_type}")



# Create a singleton instance
prompt_service = PromptService()
