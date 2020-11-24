from elasticsearch import AsyncElasticsearch

from mogship_leveling.core import config


class Database:
    client: AsyncElasticsearch = None


db = Database()


def get_client() -> AsyncElasticsearch:
    return db.client


async def connect_to_es():
    settings = config.get_settings()
    hosts = settings.es_hosts
    opts = {}
    if (settings.es_user is not None and settings.es_password is not None):
        opts["http_auth"] = (settings.es_user, settings.es_password)
    db.client = AsyncElasticsearch(hosts, **opts)


async def close_es_connection():
    await db.client.close()
