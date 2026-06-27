import logging
from dataclasses import dataclass, field
import docker
from docker.errors import NotFound, APIError
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class ContainerSpec:
    name: str
    image: str
    env: dict[str, str] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)
    cpu_quota: int = 50000
    mem_limit: str = "512m"
    network: str = "saas_net"
    volumes: dict[str, dict] = field(default_factory=dict)
    restart_policy: dict = field(default_factory=lambda: {"Name": "unless-stopped"})


class DockerManager:
    def __init__(self):
        self._client = docker.from_env()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create(self, spec: ContainerSpec) -> str:
        container = self._client.containers.run(
            spec.image,
            name=spec.name,
            detach=True,
            environment=spec.env,
            labels=spec.labels,
            cpu_quota=spec.cpu_quota,
            mem_limit=spec.mem_limit,
            network=spec.network,
            volumes=spec.volumes,
            restart_policy=spec.restart_policy,
        )
        logger.info("Created container %s (%s)", spec.name, container.short_id)
        return container.id

    def stop(self, container_id: str):
        try:
            c = self._client.containers.get(container_id)
            c.stop(timeout=30)
        except NotFound:
            logger.warning("Container %s not found for stop", container_id)

    def start(self, container_id: str):
        try:
            c = self._client.containers.get(container_id)
            c.start()
        except NotFound:
            logger.warning("Container %s not found for start", container_id)

    def restart(self, container_id: str):
        try:
            c = self._client.containers.get(container_id)
            c.restart(timeout=30)
        except NotFound:
            logger.warning("Container %s not found for restart", container_id)

    def remove(self, container_id: str, force: bool = True):
        try:
            c = self._client.containers.get(container_id)
            c.remove(force=force)
        except NotFound:
            pass

    def container_logs(self, container_id: str, tail: int = 200) -> str:
        try:
            c = self._client.containers.get(container_id)
            return c.logs(tail=tail, timestamps=True).decode("utf-8", errors="replace")
        except (NotFound, APIError):
            return ""

    def container_stats(self, container_id: str) -> dict | None:
        try:
            c = self._client.containers.get(container_id)
            raw = c.stats(stream=False)
            cpu_delta = raw["cpu_stats"]["cpu_usage"]["total_usage"] - \
                        raw["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = raw["cpu_stats"]["system_cpu_usage"] - \
                           raw["precpu_stats"]["system_cpu_usage"]
            num_cpus = raw["cpu_stats"].get("online_cpus", 1)
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0 if system_delta > 0 else 0
            memory_mb = raw["memory_stats"]["usage"] / (1024 * 1024)
            return {"cpu_percent": round(cpu_percent, 2), "memory_mb": round(memory_mb, 2)}
        except (NotFound, APIError, KeyError):
            return None
