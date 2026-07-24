import json
import os
from typing import Any

from dotenv import load_dotenv
from redis import Redis
from redis.exceptions import RedisError

load_dotenv()


class RedisCache:
    def __init__(self) -> None:
        self.redis_url = os.getenv(
            "REDIS_URL",
            "redis://localhost:6379/0",
        )

        self.client = Redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except RedisError:
            return False

    def get(self, key: str) -> Any | None:
        try:
            value = self.client.get(key)

            if value is None:
                return None

            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except RedisError as exc:
            print(f"Redis GET error for key '{key}': {exc}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        expire_seconds: int = 300,
    ) -> bool:
        try:
            serialized_value = json.dumps(
                value,
                default=str,
            )

            return bool(
                self.client.setex(
                    key,
                    expire_seconds,
                    serialized_value,
                )
            )

        except RedisError as exc:
            print(f"Redis SET error for key '{key}': {exc}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except RedisError as exc:
            print(f"Redis DELETE error for key '{key}': {exc}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        deleted_count = 0

        try:
            for key in self.client.scan_iter(match=pattern):
                deleted_count += self.client.delete(key)

        except RedisError as exc:
            print(f"Redis pattern delete error for '{pattern}': {exc}")

        return deleted_count

    def exists(self, key: str) -> bool:
        try:
            return bool(self.client.exists(key))
        except RedisError:
            return False

    def ttl(self, key: str) -> int:
        try:
            return int(self.client.ttl(key))
        except RedisError:
            return -1


redis_cache = RedisCache()