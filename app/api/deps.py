from typing import List, Optional

from fastapi import Query


def parse_list(values):
    if f'{values}'.find(',') > -1:
        return list(map(lambda x: int(x), values.split(',')))
    elif values is not None:
        return [values]
    else:
        return []


def parse_list_include_sectors(
    values: str = Query(None, alias="includeSectors")
) -> Optional[List[int]]:
    return parse_list(values)


def parse_list_exclude_sectors(
    values: str = Query(None, alias="excludeSectors")
) -> Optional[List[int]]:
    return parse_list(values)


def parse_list_include_maps(
    values: str = Query(None, alias="includeMaps")
) -> Optional[List[int]]:
    return parse_list(values)


def parse_list_exclude_maps(
    values: str = Query(None, alias="excludeMaps")
) -> Optional[List[int]]:
    return parse_list(values)


def parse_list_maps(
    values: str = Query(None, alias="maps")
) -> Optional[List[int]]:
    return parse_list(values)
