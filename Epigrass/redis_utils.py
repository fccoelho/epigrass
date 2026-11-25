"""
Central Redis configuration for Epigrass.

Epigrass uses a Redis server to share simulation state between processes
(parallel workers). All access must go through the `redisclient` defined
here, so the connection is configured in a single place, from environment
variables:

- ``EPIGRASS_REDIS_URL``   full connection URL (``redis://...``,
  ``rediss://...`` or ``unix://...``); takes precedence over the
  variables below.
- ``EPIGRASS_REDIS_HOST``  default: ``localhost``
- ``EPIGRASS_REDIS_PORT``  default: ``6379``
- ``EPIGRASS_REDIS_DB``    default: ``0``

All keys are namespaced under a prefix (``EPIGRASS_REDIS_PREFIX``,
default ``epigrass``), so start-up cleanup only ever deletes Epigrass' own
keys -- never other data that might live on the same server (the old
behavior was a blanket ``FLUSHALL`` on the default Redis, which destroys
unrelated databases).

Use :func:`key` to build namespaced key names, :func:`ensure_server` to
fail early with a helpful message, and :func:`delete_namespace` to clear
state between runs.
"""

import os

import redis

PREFIX = os.environ.get("EPIGRASS_REDIS_PREFIX", "epigrass")


def key(name: str) -> str:
    """Return `name` namespaced under the Epigrass key prefix."""
    return f"{PREFIX}:{name}"


def _build_client() -> redis.Redis:
    """Build the Redis client from environment configuration."""
    url = os.environ.get("EPIGRASS_REDIS_URL")
    if url:
        return redis.Redis.from_url(url)
    return redis.Redis(
        host=os.environ.get("EPIGRASS_REDIS_HOST", "localhost"),
        port=int(os.environ.get("EPIGRASS_REDIS_PORT", "6379")),
        db=int(os.environ.get("EPIGRASS_REDIS_DB", "0")),
    )


redisclient = _build_client()


def ensure_server() -> None:
    """Raise a helpful error if the configured Redis server is unreachable."""
    try:
        redisclient.ping()
    except redis.exceptions.ConnectionError as exc:
        cfg = redisclient.connection_pool.connection_kwargs
        target = cfg.get("path") or "{}:{}".format(
            cfg.get("host", "localhost"), cfg.get("port", 6379)
        )
        raise RuntimeError(
            f"Cannot connect to the Redis server at {target}. "
            "Epigrass uses Redis to share state between simulation processes "
            "(parallel workers). Start a Redis server, or point Epigrass at "
            "another one with EPIGRASS_REDIS_URL (or EPIGRASS_REDIS_HOST / "
            "EPIGRASS_REDIS_PORT / EPIGRASS_REDIS_DB)."
        ) from exc


def delete_namespace(client: redis.Redis = None) -> int:
    """Delete all Epigrass-namespaced keys from the server.

    Only keys under the Epigrass prefix are removed; nothing else on the
    server is touched. Returns the number of keys deleted.
    """
    client = client or redisclient
    deleted = 0
    cursor = 0
    while True:
        cursor, keys = client.scan(cursor=cursor, match=f"{PREFIX}:*", count=1000)
        if keys:
            deleted += client.delete(*keys)
        if cursor == 0:
            break
    return deleted
