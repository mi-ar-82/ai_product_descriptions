# File: app/services/ai_response_service.py

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

        # Find Body HTML
        body_start = response_text.find("BODY_HTML:")
        seo_title_start = response_text.find("SEO_TITLE:")

        if body_start != -1 and seo_title_start != -1:
            body_html = response_text[body_start + len("BODY_HTML:"):seo_title_start].strip()
            result["body_html"] = body_html

        # Find SEO Title
        seo_desc_start = response_text.find("SEO_DESCRIPTION:")
        if seo_title_start != -1 and seo_desc_start != -1:
            seo_title = response_text[seo_title_start + len("SEO_TITLE:"):seo_desc_start].strip()
            result["seo_title"] = seo_title

        # Find SEO Description
        if seo_desc_start != -1:
            seo_desc = response_text[seo_desc_start + len("SEO_DESCRIPTION:"):].strip()
            result["seo_description"] = seo_desc

        print(f"Debug: Parsed components: {list(result.keys())}")
        return result


# Create a singleton instance
ai_response_service = AIResponseService()
