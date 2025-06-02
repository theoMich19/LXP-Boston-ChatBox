"""
Utility functions for creating LangChain-compatible tools
"""

import inspect
from typing import get_type_hints
from langchain_core.tools import tool

def create_string_input_tool(func, tool_name: str = None):
    """
    Creates a string-input wrapper for any multi-parameter function.
    
    This function is essential for making multi-parameter functions compatible
    with LangChain's ConversationalAgent, which only accepts single string inputs.

    Args:
        func: The original function to wrap (should NOT have @tool decorator)
        tool_name: Optional name for the tool (defaults to func.__name__ + "_string")

    Returns:
        A LangChain tool that accepts a single string input and parses it
        to call the original multi-parameter function
    """
    # Get function info using inspection
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    param_names = list(sig.parameters.keys())

    def string_wrapper(input_string: str):
        """Parse string input and call the original function with proper parameters."""
        try:
            # Parse the input string - split by commas and strip whitespace
            values = [v.strip() for v in input_string.split(',')]

            # Validate number of parameters
            if len(values) != len(param_names):
                return f"Error: Expected {len(param_names)} comma-separated values ({', '.join(param_names)}), got {len(values)}"

            # Convert values to correct types based on type hints
            parsed_args = []
            for i, value_str in enumerate(values):
                param_name = param_names[i]
                target_type = type_hints.get(param_name, str)

                try:
                    if target_type is float:
                        parsed_args.append(float(value_str))
                    elif target_type is int:
                        # Handle both int and float strings for int parameters
                        parsed_args.append(int(float(value_str)))
                    elif target_type is bool:
                        # Handle boolean conversion
                        parsed_args.append(value_str.lower() in ('true', '1', 'yes', 'on'))
                    else:
                        # Default to string
                        parsed_args.append(value_str)
                except ValueError as ve:
                    return f"Error: Cannot convert '{value_str}' to {target_type.__name__} for parameter '{param_name}': {str(ve)}"

            # Call original function with parsed arguments
            return func(*parsed_args)

        except Exception as e:
            return f"Error: {str(e)}"

    # Set wrapper properties with improved documentation
    wrapper_name = tool_name or f"{func.__name__}_string"
    string_wrapper.__name__ = wrapper_name

    # Create example format based on parameter types
    example_values = []
    for param_name in param_names:
        target_type = type_hints.get(param_name, str)
        if target_type is float:
            example_values.append("0.0")
        elif target_type is int:
            example_values.append("123")
        elif target_type is bool:
            example_values.append("true")
        else:
            example_values.append(f"example_{param_name}")

    example_format = ", ".join(example_values)
    param_list = ", ".join(param_names)

    # Create comprehensive documentation
    string_wrapper.__doc__ = f"""{func.__doc__ or 'No description available'}

This tool expects {len(param_names)} comma-separated values in the following order:
Parameters: {param_list}

Example input format: {example_format}

Note: Values should be separated by commas. Spaces around commas are automatically trimmed."""

    return tool(string_wrapper)


def get_tmdb_genre_ids():
    """
    Helper function that returns common TMDB genre IDs for reference.

    This is useful for functions that need genre IDs as parameters.

    Returns:
        Dict: Mapping of genre names to their TMDB IDs
    """
    return {
        'Action': 28,
        'Adventure': 12,
        'Animation': 16,
        'Comedy': 35,
        'Crime': 80,
        'Documentary': 99,
        'Drama': 18,
        'Family': 10751,
        'Fantasy': 14,
        'History': 36,
        'Horror': 27,
        'Music': 10402,
        'Mystery': 9648,
        'Romance': 10749,
        'Science Fiction': 878,
        'TV Movie': 10770,
        'Thriller': 53,
        'War': 10752,
        'Western': 37
    }


def format_movie_list(movies, title="Movies"):
    """
    Helper function to format a list of movies consistently.

    Args:
        movies: List of movie dictionaries from TMDB API
        title: Title for the list

    Returns:
        Formatted string with movie information
    """
    if not movies:
        return f"No {title.lower()} found."

    result = [f"🎬 {title}:"]

    for i, movie in enumerate(movies, 1):
        movie_title = movie.get('title', 'Unknown Title')
        release_date = movie.get('release_date', 'Unknown')
        rating = movie.get('vote_average', 'N/A')
        movie_id = movie.get('id')

        # Extract year from release date
        year = release_date[:4] if release_date and release_date != 'Unknown' else 'Unknown'

        result.append(f"{i}. {movie_title} ({year}) - ⭐{rating}/10 [ID: {movie_id}]")

    return "\n".join(result)


def format_person_list(people, title="People"):
    """
    Helper function to format a list of people consistently.

    Args:
        people: List of person dictionaries from TMDB API
        title: Title for the list

    Returns:
        Formatted string with person information
    """
    if not people:
        return f"No {title.lower()} found."

    result = [f"👥 {title}:"]

    for i, person in enumerate(people, 1):
        name = person.get('name', 'Unknown Name')
        known_for_department = person.get('known_for_department', 'Unknown')
        person_id = person.get('id')
        popularity = person.get('popularity', 'N/A')

        result.append(f"{i}. {name} - {known_for_department} (Popularity: {popularity}) [ID: {person_id}]")

    return "\n".join(result)


def truncate_text(text, max_length=200):
    """
    Helper function to truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with ellipsis if needed
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length].rsplit(' ', 1)[0] + "..."


def safe_get(data, key, default='Unknown'):
    """
    Helper function to safely get values from dictionaries.

    Args:
        data: Dictionary to get value from
        key: Key to look for
        default: Default value if key not found or value is None/empty

    Returns:
        Value from dictionary or default
    """
    value = data.get(key, default)
    return value if value not in [None, '', 'null'] else default


def format_currency(amount):
    """
    Helper function to format currency amounts.

    Args:
        amount: Numeric amount

    Returns:
        Formatted currency string
    """
    if not amount or amount <= 0:
        return "Unknown"

    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.1f}K"
    else:
        return f"${amount:,}"


def parse_release_year(release_date):
    """
    Helper function to extract year from release date.

    Args:
        release_date: Release date string (YYYY-MM-DD format)

    Returns:
        Year as string or 'Unknown'
    """
    if not release_date or release_date == 'Unknown':
        return 'Unknown'

    try:
        return release_date[:4]
    except (IndexError, TypeError):
        return 'Unknown'