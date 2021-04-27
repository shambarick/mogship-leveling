from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from loguru import logger

from app.api.deps import (
    parse_list_exclude_maps,
    parse_list_exclude_sectors,
    parse_list_include_sectors,
    parse_list_maps,
    parse_list_include_maps,
)
from app.models.route import SubmarineRoute
from app.core.elasticsearch import get_client

router = APIRouter()


def get_term_query_from_list(values: List, field_name: str):
    return [
        get_term_query(value, field_name) for value in values
    ]


def get_term_query(value, field_name):
    return {
            'term': {
                field_name: value
            }
    }


def get_range_query(value, field_name):
    return {
            'range': {
                field_name: {
                    'lte': value
                }
            }
    }


@router.get("", response_model=List[SubmarineRoute])
async def get_routes(
    required_rank: Optional[int] = Query(None, alias="rank", ge=1, le=90),
    required_range: Optional[int] = Query(None, alias="range"),
    size: int = Query(100, ge=1),
    exp: Optional[int] = Query(None, alias="exp"),
    max_distance: Optional[int] = Query(None, alias="maxDistance"),
    include_sectors: Optional[List[str]] = Depends(parse_list_include_sectors),
    exclude_sectors: Optional[List[str]] = Depends(parse_list_exclude_sectors),
    maps: Optional[List[str]] = Depends(parse_list_maps),
    include_maps: Optional[List[str]] = Depends(parse_list_include_maps),
    exclude_maps: Optional[List[str]] = Depends(parse_list_exclude_maps),
    sort: str = Query('Exp,desc,Distance,asc'),
):
    query_max_distance = [get_range_query(max_distance, 'Distance')] if max_distance and max_distance > 0 else []
    query_include_sectors = get_term_query_from_list(include_sectors, 'Route')
    query_exclude_sectors = get_term_query_from_list(exclude_sectors, 'Route')
    query_include_maps = get_term_query_from_list(include_maps, 'MapID')
    query_maps = get_term_query_from_list(maps, 'MapID')
    query_exclude_maps = get_term_query_from_list(exclude_maps, 'MapID')
    query_exp = [{
        'range': {
            'Exp': {
                'gte': exp,
            },
        },
    }] if exp is not None else []
    query_rank = [{
        'range': {
            'Rank': {
                'lte': required_rank,
            },
        },
    }] if required_rank is not None else []
    query_range = [{
        'range': {
            'Range': {
                'lte': required_range,
            },
        },
    }] if required_range is not None else []

    es_sort = []
    sort_list = sort.split(",")
    if len(sort_list)%2 == 0:
        for i in range(0, len(sort_list), 2):
            es_sort.append({
                sort_list[i]: {
                    "order": sort_list[i + 1]
                }
            })
    else:
        es_sort.append({
            "Exp": {
                "order": "desc",
            }
        })
        es_sort.append({
            "Distance": {
                "order": "asc",
            }
        })

    query = {
            'size': size,
            'query': {
                'bool': {
                    'must': [
                        *query_maps
                    ],
                    'filter': [
                        *query_rank,
                        *query_range,
                        *query_exp,
                        *query_max_distance,
                        *query_include_sectors,
                        *query_include_maps,
                    ],
                    'must_not': [
                        *query_exclude_maps,
                        *query_exclude_sectors,
                    ]
                }
            },
            'sort': es_sort,
    }
    logger.info(query)

    results = await get_client().search(
        index="submarineleveling",
        body=query,
    )
    hits = [SubmarineRoute(**r['_source']) for r in results['hits']['hits']]

    return hits
