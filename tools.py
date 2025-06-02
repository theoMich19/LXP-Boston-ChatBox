"""
LXP - Advanced AI development Workshop: Chatbot tools pour TMDB API

WARNING: LangChain ConversationalAgent only accepts single input parameters for tool calling.
Use create_string_input_tool() to wrap multi-parameter functions.
"""

import os
import requests
from langchain_core.tools import tool
from utils import create_string_input_tool

# Get TMDB API key from environment
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

@tool
def search_movies(query: str) -> str:
    """Search for movies by title using TMDB API.

    Args:
        query: The movie title or search term

    Returns:
        A formatted string with search results including movie titles, release dates, and IDs
    """
    try:
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': query,
            'language': 'en-US',
            'page': 1
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get('results'):
            return f"No movies found for '{query}'. Please try a different search term."

        # Format the results
        results = []
        for movie in data['results'][:5]:  # Limit to first 5 results
            title = movie.get('title', 'Unknown Title')
            release_date = movie.get('release_date', 'Unknown')
            movie_id = movie.get('id')
            overview = movie.get('overview', 'No description available')

            # Truncate overview if too long
            if len(overview) > 100:
                overview = overview[:100] + "..."

            results.append(f"🎬 {title} ({release_date})\nID: {movie_id}\n{overview}")

        return "\n\n".join(results)

    except Exception as e:
        return f"Error searching movies: {str(e)}"

@tool
def get_movie_details(movie_id: str) -> str:
    """Get detailed information about a specific movie by ID.

    Args:
        movie_id: The TMDB movie ID

    Returns:
        A formatted string with detailed movie information
    """
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        movie = response.json()

        # Extract movie details
        title = movie.get('title', 'Unknown Title')
        release_date = movie.get('release_date', 'Unknown')
        runtime = movie.get('runtime', 'Unknown')
        rating = movie.get('vote_average', 'N/A')
        vote_count = movie.get('vote_count', 0)
        overview = movie.get('overview', 'No description available')
        budget = movie.get('budget', 0)
        revenue = movie.get('revenue', 0)

        # Get genres
        genres = [genre['name'] for genre in movie.get('genres', [])]
        genres_str = ", ".join(genres) if genres else "Unknown"

        # Get production companies
        companies = [company['name'] for company in movie.get('production_companies', [])]
        companies_str = ", ".join(companies[:3]) if companies else "Unknown"  # Limit to 3

        # Format budget and revenue
        budget_str = f"${budget:,}" if budget > 0 else "Unknown"
        revenue_str = f"${revenue:,}" if revenue > 0 else "Unknown"

        result = f"""🎬 {title} ({release_date})
⭐ Rating: {rating}/10 ({vote_count} votes)
⏱️ Runtime: {runtime} minutes
🎭 Genres: {genres_str}
🏢 Production: {companies_str}
💰 Budget: {budget_str}
💵 Revenue: {revenue_str}

📝 Overview:
{overview}"""

        return result

    except Exception as e:
        return f"Error getting movie details: {str(e)}"

def get_cast_by_movie_id(movie_id: int) -> str:
    """Get cast information for a specific movie by ID.

    Args:
        movie_id: The TMDB movie ID (integer)

    Returns:
        A formatted string with cast information
    """
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        cast = data.get('cast', [])
        crew = data.get('crew', [])

        if not cast and not crew:
            return f"No cast information found for movie ID {movie_id}."

        result = []

        # Get main cast (first 5 actors)
        if cast:
            result.append("🎭 Main Cast:")
            for actor in cast[:5]:
                name = actor.get('name', 'Unknown')
                character = actor.get('character', 'Unknown role')
                result.append(f"  • {name} as {character}")

        # Get director
        directors = [person for person in crew if person.get('job') == 'Director']
        if directors:
            result.append("\n🎬 Director(s):")
            for director in directors:
                result.append(f"  • {director.get('name', 'Unknown')}")

        return "\n".join(result)

    except Exception as e:
        return f"Error getting cast information: {str(e)}"

def get_reviews_by_movie_id(movie_id: int) -> str:
    """Get reviews for a specific movie by ID.

    Args:
        movie_id: The TMDB movie ID (integer)

    Returns:
        A formatted string with movie reviews
    """
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}/reviews"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'page': 1
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        reviews = data.get('results', [])

        if not reviews:
            return f"No reviews found for movie ID {movie_id}."

        result = ["📝 Movie Reviews:"]

        for review in reviews[:3]:  # Limit to 3 reviews
            author = review.get('author', 'Anonymous')
            content = review.get('content', 'No content available')
            rating = review.get('author_details', {}).get('rating')

            # Truncate long reviews
            if len(content) > 200:
                content = content[:200] + "..."

            rating_str = f" ({rating}/10)" if rating else ""
            result.append(f"\n👤 {author}{rating_str}:")
            result.append(f"   {content}")

        return "\n".join(result)

    except Exception as e:
        return f"Error getting reviews: {str(e)}"

@tool
def get_popular_movies() -> str:
    """Get currently popular movies from TMDB.

    Returns:
        A formatted string with popular movies list
    """
    try:
        url = f"{TMDB_BASE_URL}/movie/popular"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'page': 1
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        movies = data.get('results', [])

        if not movies:
            return "No popular movies found."

        result = ["🔥 Popular Movies:"]

        for i, movie in enumerate(movies[:10], 1):  # Top 10
            title = movie.get('title', 'Unknown Title')
            release_date = movie.get('release_date', 'Unknown')
            rating = movie.get('vote_average', 'N/A')
            movie_id = movie.get('id')

            result.append(f"{i}. {title} ({release_date}) - ⭐{rating}/10 [ID: {movie_id}]")

        return "\n".join(result)

    except Exception as e:
        return f"Error getting popular movies: {str(e)}"

@tool
def get_trending_movies() -> str:
    """Get trending movies for today from TMDB.

    Returns:
        A formatted string with trending movies list
    """
    try:
        url = f"{TMDB_BASE_URL}/trending/movie/day"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        movies = data.get('results', [])

        if not movies:
            return "No trending movies found."

        result = ["📈 Trending Movies Today:"]

        for i, movie in enumerate(movies[:10], 1):  # Top 10
            title = movie.get('title', 'Unknown Title')
            release_date = movie.get('release_date', 'Unknown')
            rating = movie.get('vote_average', 'N/A')
            movie_id = movie.get('id')

            result.append(f"{i}. {title} ({release_date}) - ⭐{rating}/10 [ID: {movie_id}]")

        return "\n".join(result)

    except Exception as e:
        return f"Error getting trending movies: {str(e)}"

def discover_movies_by_genre_and_year(genre_id: int, year: int) -> str:
    """Discover movies by genre and release year.

    Args:
        genre_id: The TMDB genre ID (e.g., 28 for Action, 35 for Comedy)
        year: The release year (e.g., 2023)

    Returns:
        A formatted string with discovered movies
    """
    try:
        url = f"{TMDB_BASE_URL}/discover/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US',
            'with_genres': genre_id,
            'year': year,
            'sort_by': 'popularity.desc',
            'page': 1
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        movies = data.get('results', [])

        if not movies:
            return f"No movies found for genre ID {genre_id} in year {year}."

        # Get genre name
        genre_url = f"{TMDB_BASE_URL}/genre/movie/list"
        genre_params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
        genre_response = requests.get(genre_url, params=genre_params, timeout=10)
        genre_data = genre_response.json()

        genre_name = "Unknown Genre"
        for genre in genre_data.get('genres', []):
            if genre['id'] == genre_id:
                genre_name = genre['name']
                break

        result = [f"🎭 {genre_name} Movies from {year}:"]

        for i, movie in enumerate(movies[:8], 1):  # Top 8
            title = movie.get('title', 'Unknown Title')
            rating = movie.get('vote_average', 'N/A')
            movie_id = movie.get('id')

            result.append(f"{i}. {title} - ⭐{rating}/10 [ID: {movie_id}]")

        return "\n".join(result)

    except Exception as e:
        return f"Error discovering movies: {str(e)}"

def get_person_info(person_id: int) -> str:
    """Get detailed information about a person (actor, director, etc.) by ID.

    Args:
        person_id: The TMDB person ID (integer)

    Returns:
        A formatted string with person information
    """
    try:
        url = f"{TMDB_BASE_URL}/person/{person_id}"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        person = response.json()

        name = person.get('name', 'Unknown')
        birthday = person.get('birthday', 'Unknown')
        place_of_birth = person.get('place_of_birth', 'Unknown')
        biography = person.get('biography', 'No biography available')
        known_for = person.get('known_for_department', 'Unknown')
        popularity = person.get('popularity', 'N/A')

        # Truncate biography if too long
        if len(biography) > 300:
            biography = biography[:300] + "..."

        result = f"""👤 {name}
🎭 Known for: {known_for}
🎂 Born: {birthday}
📍 Place of Birth: {place_of_birth}
📊 Popularity: {popularity}

📖 Biography:
{biography}"""

        return result

    except Exception as e:
        return f"Error getting person information: {str(e)}"

def get_person_credits(person_id: int) -> str:
    """Get movie credits for a person (actor, director, etc.) by ID.

    Args:
        person_id: The TMDB person ID (integer)

    Returns:
        A formatted string with person's movie credits
    """
    try:
        url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits"
        params = {
            'api_key': TMDB_API_KEY,
            'language': 'en-US'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        cast = data.get('cast', [])
        crew = data.get('crew', [])

        result = []

        # Get person name
        person_url = f"{TMDB_BASE_URL}/person/{person_id}"
        person_response = requests.get(person_url, params={'api_key': TMDB_API_KEY}, timeout=10)
        person_name = person_response.json().get('name', 'Unknown Person')

        result.append(f"🎬 {person_name}'s Movie Credits:")

        # Acting credits (top 5 most popular)
        if cast:
            cast_sorted = sorted(cast, key=lambda x: x.get('popularity', 0), reverse=True)
            result.append("\n🎭 As Actor:")
            for movie in cast_sorted[:5]:
                title = movie.get('title', 'Unknown')
                character = movie.get('character', 'Unknown role')
                release_date = movie.get('release_date', 'Unknown')[:4]  # Just year
                result.append(f"  • {title} ({release_date}) as {character}")

        # Directing credits
        directing_credits = [movie for movie in crew if movie.get('job') == 'Director']
        if directing_credits:
            result.append("\n🎬 As Director:")
            for movie in directing_credits[:5]:
                title = movie.get('title', 'Unknown')
                release_date = movie.get('release_date', 'Unknown')[:4]  # Just year
                result.append(f"  • {title} ({release_date})")

        return "\n".join(result)

    except Exception as e:
        return f"Error getting person credits: {str(e)}"

# Create the string input tool versions for LangChain
get_movie_cast = create_string_input_tool(get_cast_by_movie_id, "get_movie_cast")
get_movie_reviews = create_string_input_tool(get_reviews_by_movie_id, "get_movie_reviews")
discover_movies_by_genre = create_string_input_tool(discover_movies_by_genre_and_year, "discover_movies_by_genre")
get_person_details = create_string_input_tool(get_person_info, "get_person_details")
get_person_movie_credits = create_string_input_tool(get_person_credits, "get_person_movie_credits")