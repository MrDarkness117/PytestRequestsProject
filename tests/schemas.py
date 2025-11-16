# Схемы проверки API

schema_chat_completion = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "object": {"type": "string"},
        "created": {"type": "integer"},
        "model": {"type": "string"},
        "choices": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "message": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["role", "content"]
                    },
                    "finish_reason": {"type": "string"}
                },
                "required": ["index", "message", "finish_reason"]
            }
        },
        "usage": {
            "type": "object",
            "properties": {
                "prompt_tokens": {"type": "integer"},
                "completion_tokens": {"type": "integer"},
                "total_tokens": {"type": "integer"}
            },
            "required": ["prompt_tokens", "completion_tokens", "total_tokens"]
        }
    },
    "required": ["id", "object", "created", "model", "choices", "usage"]
}
