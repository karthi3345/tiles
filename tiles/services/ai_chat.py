import requests
from django.conf import settings

SYSTEM_PROMPT = """You are Studio Mathri AI, an expert tile industry assistant. You know everything about:
- Ceramic, porcelain, vitrified, mosaic, natural stone tiles
- Floor tiles, wall tiles, special-purpose tiles (pool, parking, outdoor, anti-slip)
- Tile manufacturing in China, India, Brazil, Spain, Italy, Turkey, Vietnam, USA, Mexico, Indonesia
- Tile effects: marble, wood, stone, concrete, geometric, solid, metallic, terracotta
- Tile finishes: glossy, matte, polished, textured, rustic, anti-slip
- Tile sizes from small mosaics to 3200x1600mm slabs
- Installation, grouting, maintenance
- Market data, pricing, export/import
- Location-specific tile availability (states, cities, and villages)
Be concise, structured, and helpful. Use bullet points when listing items.
"""


def _extract_text(result):
    """
    Try every known Workers AI / OpenAI-compatible response shape and
    return the extracted text, or '' if nothing matched.
    """
    if result is None:
        return ""

    # Some models return the result itself as a plain string
    if isinstance(result, str):
        return result

    if not isinstance(result, dict):
        return ""

    # New Workers AI chat-completions format: result.choices[0].message.content
    choices = result.get("choices")
    if choices:
        message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        content = message.get("content", "")
        # content can be a string OR a list of content-part dicts
        if isinstance(content, list):
            text = "".join(
                part.get("text", "") for part in content if isinstance(part, dict)
            )
            if text:
                return text
        elif isinstance(content, str) and content:
            return content
        # some function-calling models put text under choices[0].text instead
        alt = choices[0].get("text", "") if isinstance(choices[0], dict) else ""
        if alt:
            return alt

    # Older Workers AI text-generation format
    if result.get("response"):
        return result["response"]

    if result.get("text"):
        return result["text"]

    if result.get("output_text"):
        return result["output_text"]

    # Some models nest under result.output[0].content[0].text
    output = result.get("output")
    if isinstance(output, list) and output:
        first = output[0]
        if isinstance(first, dict):
            content = first.get("content")
            if isinstance(content, list) and content:
                for part in content:
                    if isinstance(part, dict) and part.get("text"):
                        return part["text"]
            elif isinstance(content, str) and content:
                return content

    return ""


class CloudflareMistralChat:
    def __init__(self):
        self.account_id = settings.CF_ACCOUNT_ID
        self.api_token = settings.CF_API_TOKEN
        self.model = settings.CF_CHAT_MODEL
        self.base_url = settings.CF_BASE_URL

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def is_configured(self):
        return bool(self.account_id and self.api_token)

    def chat(self, message, history=None):
        if not self.is_configured():
            return {
                "success": False,
                "response": "",
                "error": "Cloudflare AI not configured."
            }

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        if history:
            messages.extend(history[-10:])

        messages.append({
            "role": "user",
            "content": message
        })

        try:
            resp = requests.post(
                f"{self.base_url}/{self.model}",
                headers=self.headers,
                json={
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7
                },
                timeout=30,
            )

            resp.raise_for_status()

            print("Status:", resp.status_code)
            print(resp.text)

            data = resp.json()

            if data.get("success"):
                result = data.get("result", {})
                response = _extract_text(result)

                if not response:
                    # Don't silently report success with nothing to show —
                    # log the raw shape so it's obvious what to add support for.
                    print("WARNING: chat succeeded but no text could be extracted.")
                    print("Raw result was:", result)
                    return {
                        "success": False,
                        "response": "",
                        "error": "AI responded but returned no readable text (unrecognized response shape).",
                    }

                return {
                    "success": True,
                    "response": response,
                    "error": None,
                }

            errors = data.get("errors", [])

            return {
                "success": False,
                "response": "",
                "error": errors[0].get("message", "API Error") if errors else "Failed",
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "response": "",
                "error": "Request timed out",
            }

        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "response": "",
                "error": f"HTTP Error: {e}",
            }

        except Exception as e:
            return {
                "success": False,
                "response": "",
                "error": str(e),
            }


chat_service = CloudflareMistralChat()