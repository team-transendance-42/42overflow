from dataclasses import dataclass, field
import time


@dataclass
class Metrics:
    retrieve_total: int = 0
    retrieve_errors: int = 0
    bm25_only_fallbacks: int = 0
    corpus_size: int = 0
    last_sync_at: float | None = None
    started_at: float = field(default_factory=time.time)

    def uptime_seconds(self) -> float:
        return round(time.time() - self.started_at, 1)
