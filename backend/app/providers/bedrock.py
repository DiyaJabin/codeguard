class BedrockReviewProvider:
    """Guardrail placeholder: paid inference is never reachable in local defaults."""
    name="bedrock"
    def __init__(self,*args,**kwargs):
        raise RuntimeError("Bedrock is disabled by default; review cost, quotas, IAM, and model access before enabling.")
