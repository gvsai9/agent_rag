from models.search_result import SearchResult
def deduplicate_sources(
    results: list[SearchResult]
) -> list[SearchResult]:

    seen = set()

    unique = []

    for result in results:

        if result.paper_id in seen:
            continue

        seen.add(
            result.paper_id
        )

        unique.append(
            result
        )

    return unique