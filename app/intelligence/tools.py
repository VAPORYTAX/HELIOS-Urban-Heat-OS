TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_context_packet",
            "description": "Return the already-built HELIOS evidence packet. Use it instead of inventing facts.",
            "parameters": {"type":"object","properties":{"packet_id":{"type":"string"}},"required":["packet_id"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_optimizer_selection",
            "description": "Explain a selected intervention using stored optimizer evidence only.",
            "parameters": {
                "type":"object",
                "properties":{"run_id":{"type":"string"},"cell_id":{"type":"string"}},
                "required":["run_id","cell_id"],
            },
        },
    },
]
