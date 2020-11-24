from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from loguru import logger

from mogship_leveling.api.deps import (
    parse_list_exclude_maps,
    parse_list_exclude_sectors,
    parse_list_include_sectors,
    parse_list_maps,
    parse_list_include_maps
)
from mogship_leveling.models.route import SubmarineRoute
from mogship_leveling.core.elasticsearch import get_client

router = APIRouter()


def get_term_query_from_list(values: List, field_name: str):
    return [
        {
            'term': {
                field_name: value
            }
        } for value in values
    ]


@router.get("", response_model=List[SubmarineRoute])
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
    query_include_sectors = get_term_query_from_list(include_sectors, 'Route')
    query_exclude_sectors = get_term_query_from_list(exclude_sectors, 'Route')
    query_include_maps = get_term_query_from_list(include_maps, 'MapID')
    query_maps = get_term_query_from_list(maps, 'MapID')
    query_exclude_maps = get_term_query_from_list(exclude_maps, 'MapID')

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

    logger.bind(payload=query).debug('ES query')

    results = await get_client().search(
        index="submarinelevelings-1",
        body=query,
    )
    hits = [SubmarineRoute(**r['_source']) for r in results['hits']['hits']]

    return hits