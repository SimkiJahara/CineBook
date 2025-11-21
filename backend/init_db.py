"""
Database Initialization Script
Populates the CineBook database with genres, movies, cast & reviews
Run once after starting the project
"""
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random

# Correct imports — MovieCast is a real model, not an association table
from app.models.movie import Base, Movie, Genre, Review, movie_genre_association, MovieCast
from app.database import engine


print("=" * 70)
print("CINEBOOK MOVIE MODULE - DATABASE INITIALIZATION")
print("=" * 70)


def init_database():
    print("Creating tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    print("Tables ready")

    db = Session(engine)

    try:
        # Prevent running twice
        if db.query(Genre).count() > 0 or db.query(Movie).count() > 0:
            print("Data already exists. Skipping initialization.")
            return

        print("\nCreating genres...")
        genres_data = [
            "Action", "Comedy", "Drama", "Horror", "Romance",
            "Sci-Fi", "Thriller", "Animation", "Adventure",
            "Fantasy", "Crime", "Documentary"
        ]
        genre_objs = []
        for name in genres_data:
            genre = Genre(name=name, description=f"Amazing {name.lower()} movies")
            db.add(genre)
            genre_objs.append(genre)
        db.flush()
        print(f"Created {len(genre_objs)} genres")

        print("\nCreating 8 rich sample movies...")
        movies_data = [
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F001",
                "title": "The Epic Journey",
                "posterurl": "https://via.placeholder.com/300x450/003366/FFFFFF?text=The+Epic+Journey",
                "language": "English",
                "lengthmin": 142,
                "rating": "PG-13",
                "releasedate": date.today() - timedelta(days=30),
                "description": "An epic quest across forgotten lands to find the lost crystal of power.",
                "director": "James Cameron",
                "trailerurl": "https://youtube.com/watch?v=epic2025",
                "genres": ["Action", "Adventure"],
                "cast": ["Chris Hemsworth", "Natalie Portman", "Tom Hardy"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F002",
                "title": "Laugh Out Loud",
                "posterurl": "https://via.placeholder.com/300x450/FFCC00/000000?text=Laugh+Out+Loud",
                "language": "English",
                "lengthmin": 98,
                "rating": "PG",
                "releasedate": date.today() - timedelta(days=15),
                "description": "The ultimate feel-good comedy of the year!",
                "director": "Judd Apatow",
                "trailerurl": "https://youtube.com/watch?v=lolcomedy",
                "genres": ["Comedy"],
                "cast": ["Kevin Hart", "Tiffany Haddish", "Will Ferrell"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F003",
                "title": "Dark Shadows",
                "posterurl": "https://via.placeholder.com/300x450/000000/FFFFFF?text=Dark+Shadows",
                "language": "English",
                "lengthmin": 115,
                "rating": "R",
                "releasedate": date.today() - timedelta(days=5),
                "description": "Evil never sleeps. A terrifying horror masterpiece.",
                "director": "Jordan Peele",
                "trailerurl": "https://youtube.com/watch?v=darkshadows",
                "genres": ["Horror", "Thriller"],
                "cast": ["Lupita Nyong'o", "Winston Duke", "Elisabeth Moss"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F004",
                "title": "Love in Paris",
                "posterurl": "https://via.placeholder.com/300x450/FF69B4/FFFFFF?text=Love+in+Paris",
                "language": "English",
                "lengthmin": 105,
                "rating": "PG-13",
                "releasedate": date.today() - timedelta(days=20),
                "description": "A romantic story that proves love finds you when you least expect it.",
                "director": "Nancy Meyers",
                "trailerurl": "https://youtube.com/watch?v=loveinparis",
                "genres": ["Romance", "Comedy"],
                "cast": ["Emma Stone", "Ryan Gosling", "Rachel McAdams"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F005",
                "title": "Future World 2099",
                "posterurl": "https://via.placeholder.com/300x450/0D1B2A/00FF00?text=Future+World+2099",
                "language": "English",
                "lengthmin": 135,
                "rating": "PG-13",
                "releasedate": date.today() + timedelta(days=10),
                "description": "In a broken future, hope is the ultimate rebellion.",
                "director": "Denis Villeneuve",
                "trailerurl": "https://youtube.com/watch?v=future2099",
                "genres": ["Sci-Fi", "Action"],
                "cast": ["Timothée Chalamet", "Zendaya", "Oscar Isaac"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F006",
                "title": "The Family Secret",
                "posterurl": "https://via.placeholder.com/300x450/4A4E69/FFFFFF?text=Family+Secret",
                "language": "English",
                "lengthmin": 118,
                "rating": "PG-13",
                "releasedate": date.today() - timedelta(days=2),
                "description": "Some secrets destroy families. Others save them.",
                "director": "Greta Gerwig",
                "trailerurl": "https://youtube.com/watch?v=familysecret",
                "genres": ["Drama"],
                "cast": ["Saoirse Ronan", "Florence Pugh", "Timothée Chalamet"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F007",
                "title": "Bangla Bhalobasha",
                "posterurl": "https://via.placeholder.com/300x450/DC143C/FFFFFF?text=Bangla+Bhalobasha",
                "language": "Bangla",
                "lengthmin": 125,
                "rating": "PG",
                "releasedate": date.today() - timedelta(days=10),
                "description": "একটি অসাধারণ বাংলা প্রেম কাহিনী যা হৃদয় ছুঁয়ে যায়।",
                "director": "Anik Dutta",
                "trailerurl": "https://youtube.com/watch?v=banglabhalobasha",
                "genres": ["Romance", "Drama"],
                "cast": ["Jaya Ahsan", "Chanchal Chowdhury", "Mosharraf Karim"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F008",
                "title": "Space Odyssey 3000",
                "posterurl": "https://via.placeholder.com/300x450/000033/00FFFF?text=Space+Odyssey+3000",
                "language": "English",
                "lengthmin": 160,
                "rating": "PG-13",
                "releasedate": date.today() + timedelta(days=20),
                "description": "Humanity's final frontier begins now.",
                "director": "Christopher Nolan",
                "trailerurl": "https://youtube.com/watch?v=space3000",
                "genres": ["Sci-Fi", "Adventure"],
                "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"]
            }
        ]

        movies = []
        for data in movies_data:
            genre_names = data.pop("genres")
            cast_list = data.pop("cast")

            movie = Movie(**data)
            movie.genres = [g for g in genre_objs if g.name in genre_names]
            db.add(movie)
            db.flush()

            # Add cast using the proper MovieCast model
            for actor in cast_list:
                db.add(MovieCast(movie_eidr=movie.eidr, cast_member=actor))

            movies.append(movie)

        print(f"Created {len(movies)} movies with genres & cast")

        # Sample reviews
        print("\nAdding sample reviews...")
        review_texts = [
            "Mind-blowing! Best movie of the year!",
            "Absolutely loved it. Cried and laughed.",
            "A masterpiece. 10/10 would watch again.",
            "The acting was phenomenal!",
            "This deserves all the awards.",
            "Incredible visuals and story.",
            "One of the greatest films ever made.",
            "Touched my heart deeply."
        ]

        review_count = 0
        for movie in movies[:6]:
            for _ in range(random.randint(3, 8)):
                review = Review(
                    movie_eidr=movie.eidr,
                    user_id=random.randint(1, 50),
                    rating=round(random.uniform(3.8, 5.0), 1),
                    review_text=random.choice(review_texts)
                )
                db.add(review)
                review_count += 1

        db.commit()
        print(f"Added {review_count} realistic reviews")

        print("\n" + "SUCCESS: Database initialized perfectly!")
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Genres      : {db.query(Genre).count()}")
        print(f"Movies      : {db.query(Movie).count()}")
        print(f"Cast Entries: {db.query(MovieCast).count()}")
        print(f"Reviews     : {db.query(Review).count()}")
        print("=" * 70)
        print("Your CineBook backend is READY!")
        print("Run: uvicorn app.main:app --reload")
        print("Docs: http://localhost:8000/docs")
        print("=" * 70)

    except Exception as e:
        print(f"\nERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()