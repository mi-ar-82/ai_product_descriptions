# File: app/services/ai_response_service.py
import json
from typing import Dict


class AIResponseService:
    @staticmethod
    def parse_ai_response(response_text: str) -> Dict[str, str]:
        """Parse the AI response to extract the three components."""
        print(f"Debug: Parsing AI response, type: {type(response_text)}")

        result = {
            "body_html": "",
            "seo_title": "",
            "seo_description": ""
        }

        try:
            # Try to parse as JSON first (preferred method)
            data = json.loads(response_text)

            # Extract components directly from JSON
            if "BODY_HTML" in data:
                result["body_html"] = data["BODY_HTML"]

            if "SEO_TITLE" in data:
                result["seo_title"] = data["SEO_TITLE"]

            if "SEO_DESCRIPTION" in data:
                result["seo_description"] = data["SEO_DESCRIPTION"]

            print(f"Debug: Successfully parsed JSON response")

        except json.JSONDecodeError as e:
            print(f"Debug: JSON parsing failed: {str(e)}")
            print(f"Debug: Raw response excerpt: {response_text[:100]}...")

            # Fall back to string extraction if JSON parsing fails
            # Find Body HTML
            body_start = response_text.find('"BODY_HTML":"')
            seo_title_start = response_text.find('"SEO_TITLE":"')

            if body_start != -1 and seo_title_start != -1:
                # Extract content between quotes
                content_start = body_start + len('"BODY_HTML":"')
                content_end = response_text.find('"', content_start)
                if content_end != -1:
                    result["body_html"] = response_text[content_start:content_end]

            # Find SEO Title
            seo_desc_start = response_text.find('"SEO_DESCRIPTION":"')
            if seo_title_start != -1 and seo_desc_start != -1:
                # Extract content between quotes
                content_start = seo_title_start + len('"SEO_TITLE":"')
                content_end = response_text.find('"', content_start)
                if content_end != -1:
                    result["seo_title"] = response_text[content_start:content_end]

            # Find SEO Description
            if seo_desc_start != -1:
                # Extract content between quotes
                content_start = seo_desc_start + len('"SEO_DESCRIPTION":"')
                content_end = response_text.find('"', content_start)
                if content_end != -1:
                    result["seo_description"] = response_text[content_start:content_end]

        # Print debug information about extracted content
        print(
            f"Debug: Extracted body_html (first 50 chars): {result['body_html'][:50] if result['body_html'] else ''}...")
        print(f"Debug: Extracted seo_title: {result['seo_title']}")
        print(f"Debug: Extracted seo_description: {result['seo_description']}")

        return result


# Create a singleton instance
ai_response_service = AIResponseService()
