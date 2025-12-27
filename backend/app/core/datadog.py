"""
Datadog Observability Setup.

Initializes tracing and custom metrics for LLM observability.
"""
import os
from ddtrace import tracer, patch_all
from ddtrace.contrib.trace_utils import set_flattened_tags


def init_datadog():
    """
    Initialize Datadog tracing.
    
    Call this at application startup.
    """
    service_name = os.getenv("DD_SERVICE", "pulsetrade-crypto")
    env = os.getenv("DD_ENV", "development")
    
    # Patch all supported libraries
    patch_all()
    
    # Configure tracer
    tracer.configure(
        hostname=os.getenv("DD_AGENT_HOST", "localhost"),
        port=int(os.getenv("DD_TRACE_AGENT_PORT", "8126")),
    )
    
    # Set global tags
    tracer.set_tags({
        "service": service_name,
        "env": env,
        "version": "2.0.0",
    })
    
    print(f"[Datadog] Tracing initialized for {service_name} ({env})")


def trace_llm_call(model: str, prompt_tokens: int, completion_tokens: int, latency_ms: float):
    """
    Add LLM-specific tags to current span.
    
    Args:
        model: Model name (e.g., "gemini-1.5-flash")
        prompt_tokens: Input token count
        completion_tokens: Output token count
        latency_ms: Response latency in milliseconds
    """
    span = tracer.current_span()
    if span:
        span.set_tag("llm.model", model)
        span.set_tag("llm.prompt_tokens", prompt_tokens)
        span.set_tag("llm.completion_tokens", completion_tokens)
        span.set_tag("llm.total_tokens", prompt_tokens + completion_tokens)
        span.set_tag("llm.latency_ms", latency_ms)


def trace_voice_call(text_length: int, audio_bytes: int, latency_ms: float):
    """
    Add voice synthesis tags to current span.
    
    Args:
        text_length: Input text character count
        audio_bytes: Output audio size in bytes
        latency_ms: Synthesis latency in milliseconds
    """
    span = tracer.current_span()
    if span:
        span.set_tag("voice.text_length", text_length)
        span.set_tag("voice.audio_bytes", audio_bytes)
        span.set_tag("voice.latency_ms", latency_ms)
