from pathlib import Path
import yaml


class BudgetExceeded(Exception):
    pass


def load_settings(config_path: Path) -> dict:
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class BudgetTracker:
    def __init__(self, settings: dict):
        self._limits: dict = settings.get("max_requests_per_run", {})
        self._used: dict = {}
        self._max_runtime: int = settings.get("max_runtime_seconds", 300)
        self._enabled: dict = {
            k.removeprefix("enable_service_"): v
            for k, v in settings.items()
            if k.startswith("enable_service_")
        }

    def check_service(self, service: str):
        if not self._enabled.get(service, True):
            raise BudgetExceeded(f"service '{service}' disabled in settings.yaml")

    def consume(self, service: str, n: int = 1):
        self.check_service(service)
        current = self._used.get(service, 0) + n
        limit = self._limits.get(service)
        if limit is not None and current > limit:
            raise BudgetExceeded(
                f"budget exceeded for '{service}': {current}/{limit} requests"
            )
        self._used[service] = current

    def remaining(self, service: str) -> int | None:
        limit = self._limits.get(service)
        if limit is None:
            return None
        return limit - self._used.get(service, 0)

    @property
    def max_runtime(self) -> int:
        return self._max_runtime
