---
trigger: glob
globs: tools/*
---

- All tool definitions must contain a docstring with Args and their types. For example:
    """
    Fetches the latest `count` setlists for the given artist name using setlist.fm API.

    Args:
        artist_name (str): The name of the artist to search for.
        count (int, optional): How many of the latest setlists to retrieve. Defaults to 1.

    Returns:
        list: A list of dicts, each containing setlist info.
    """