from pprint import pprint
from typing import List, Optional
import sys

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Query, Depends

from mogship_leveling.models.route import SubmarineRoute

app = FastAPI()

es = AsyncElasticsearch(
    ['xxxx'],
    http_auth=('elastic', 'xxxx')
)


def parse_list(values):
    if f'{values}'.find(',') > -1:
        return list(map(lambda x: int(x), values.split(',')))
    elif values is not None:
        return [values]
    else:
        return []


def parse_list_include_sectors(values: str = Query(None, alias="includeSectors")) -> Optional[List[int]]:
    return parse_list(values)


def parse_list_exclude_sectors(values: str = Query(None, alias="excludeSectors")) -> Optional[List[int]]:
    return parse_list(values)


def parse_list_include_maps(values: str = Query(None, alias="includeMaps")) -> Optional[List[int]]:
    return parse_list(values)


def parse_list_exclude_maps(values: str = Query(None, alias="excludeMaps")) -> Optional[List[int]]:
    return parse_list(values)

def parse_list_maps(values: str = Query(None, alias="maps")) -> Optional[List[int]]:
    return parse_list(values)


@app.on_event("shutdown")
async def app_shutdown():
    await es.close()

@app.get("/routes")
async def get_routes(
    required_rank: int = Query(1, alias="rank", ge=1, le=75),
    required_range: int = Query(70, alias="range"),
    size: int = Query(100, ge=1),
    include_sectors: Optional[List[str]] = Depends(parse_list_include_sectors),
    exclude_sectors: Optional[List[str]] = Depends(parse_list_exclude_sectors),
    maps: Optional[List[str]] = Depends(parse_list_maps),
    include_maps: Optional[List[str]] = Depends(parse_list_include_maps),
    exclude_maps: Optional[List[str]] = Depends(parse_list_exclude_maps),
):
    query_include_sectors = [
        {
            'term': {
                'Route': r
            }
        } for r in include_sectors
    ]
    
    query_exclude_sectors = [
        {
            'term': {
                'Route': r
            }
        } for r in exclude_sectors
    ]

    query_include_maps = [
        {
            'term': {
                'MapID': m,
            },
        } for m in include_maps
    ]

    query_maps = [
        {
            'term': {
                'MapID': m,
            },
        } for m in maps
    ]

    query_exclude_maps = [
        {
            'term': {
                'MapID': m,
            },
        } for m in exclude_maps
    ]

    query = {
            'size': size,
            'query': {
                'bool': {
                    'must': [
                        *query_maps
                    ],
                    'filter': [
                        {
                            'range': {
                                'Rank': {
                                    'lte': required_rank
                                }
                            }
                        },
                        {
                            'range': {
                                'Range': {
                                    'lte': required_range
                                }
                            }
                        },
                        *query_include_sectors,
                        *query_include_maps,
                    ],
                    'must_not': [
                        *query_exclude_maps,
                        *query_exclude_sectors,
                    ]
                }
            },
            'sort': [
                {
                    'Exp': {
                        'order': 'DESC'
                    }
                },
                {
                    'Distance': {
                        'order': 'ASC'
                    }
                },
            ]
    }

    pprint(query)

    results = await es.search(
        index="submarinelevelings-1",
        body = query
    )
    hits = [SubmarineRoute(**r['_source']) for r in results['hits']['hits']]

    return hits