class AgentException(Exception):
    """Raised when a Groq LLM agent encounters an error."""

    def __init__(self, agent_name: str, detail: str) -> None:
        self.agent_name = agent_name
        self.detail = detail
        super().__init__(f"[{agent_name}] {detail}")
