from prometheus_client import Counter, Histogram
import time

class MetricsCollector:
    def __init__(self):
        self.research_requests = Counter(
            'research_requests_total',
            'Total research requests'
        )
        self.agent_execution_time = Histogram(
            'agent_execution_seconds',
            'Time spent in agent execution'
        )

metrics = MetricsCollector() 