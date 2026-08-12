from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

def setup_tracing():
    """Configures OpenTelemetry for Distributed Tracing."""
    provider = TracerProvider()
    
    # In production, this would export to Jaeger, Zipkin, or Datadog
    # For now, we export to console for visibility
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(__name__)

tracer = setup_tracing()
