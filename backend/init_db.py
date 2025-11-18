"""
Database Initialization Script
Creates tables and populates with sample data
"""
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random
from app.models.movie import Base, Movie, Genre, Review, movie_genre_association, movie_cast_association
from app.database import engine


print("=" * 50)
print("CINEBOOK DATABASE INITIALIZATION")
print("=" * 50)


def init_database():
    """Initialize database with tables and sample data"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")

    db = Session(engine)

    try:
        # FIXED: was db.query(db.query(Genre).count()) → wrong!
        existing_genres = db.query(Genre).count()
        if existing_genres > 0:
            print("Database already contains data. Skipping initialization.")
            return

        # Create genres
        print("\nCreating genres...")
        genres_data = [
            {"name": "Action", "description": "Action-packed adventures and thrillers"},
            {"name": "Comedy", "description": "Funny and entertaining movies"},
            {"name": "Drama", "description": "Serious and emotional storytelling"},
            {"name": "Horror", "description": "Scary and suspenseful films"},
            {"name": "Romance", "description": "Love stories and romantic films"},
            {"name": "Sci-Fi", "description": "Science fiction and futuristic themes"},
            {"name": "Thriller", "description": "Suspenseful and exciting films"},
            {"name": "Animation", "description": "Animated movies for all ages"},
            {"name": "Adventure", "description": "Exciting journeys and quests"},
            {"name": "Fantasy", "description": "Magical and fantastical worlds"},
            {"name": "Crime", "description": "Crime and detective stories"},
            {"name": "Documentary", "description": "Non-fiction and educational films"},
        ]

        genres = []
        for genre_data in genres_data:
            genre = Genre(**genre_data)
            db.add(genre)
            genres.append(genre)
        db.flush()
        print(f"Created {len(genres)} genres")

        # Create sample movies
        print("\nCreating sample movies...")
        movies_data = [
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F001",
                "title": "The Epic Journey",
                "poster_url": "https://via.placeholder.com/300x450?text=Epic+Journey",
                "language": "English",
                "duration_min": 142,
                "rating": "PG-13",
                "release_date": date.today() - timedelta(days=30),
                "description": "An epic adventure across uncharted territories",
                "director": "James Cameron",
                "trailer_url": "https://youtube.com/watch?v=example1",
                "genre_names": ["Action", "Adventure"],
                "cast": ["John Doe", "Jane Smith", "Bob Johnson"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F002",
                "title": "Laugh Out Loud",
                "poster_url": "https://via.placeholder.com/300x450?text=Laugh+Out+Loud",
                "language": "English",
                "duration_min": 98,
                "rating": "PG",
                "release_date": date.today() - timedelta(days=15),
                "description": "A hilarious comedy that will keep you laughing",
                "director": "Judd Apatow",
                "trailer_url": "https://youtube.com/watch?v=example2",
                "genre_names": ["Comedy"],
                "cast": ["Chris Rock", "Amy Schumer", "Kevin Hart"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F003",
                "title": "Dark Shadows",
                "poster_url": "https://via.placeholder.com/300x450?text=Dark+Shadows",
                "language": "English",
                "duration_min": 115,
                "rating": "R",
                "release_date": date.today() - timedelta(days=5),
                "description": "A chilling horror experience that will haunt your dreams",
                "director": "Jordan Peele",
                "trailer_url": "https://youtube.com/watch?v=example3",
                "genre_names": ["Horror", "Thriller"],
                "cast": ["Lupita Nyong'o", "Winston Duke"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F004",
                "title": "Love in Paris",
                "poster_url": "https://via.placeholder.com/300x450?text=Love+in+Paris",
                "language": "English",
                "duration_min": 105,
                "rating": "PG-13",
                "release_date": date.today() - timedelta(days=20),
                "description": "A romantic tale set in the beautiful city of Paris",
                "director": "Nancy Meyers",
                "trailer_url": "https://youtube.com/watch?v=example4",
                "genre_names": ["Romance", "Comedy"],
                "cast": ["Emma Stone", "Ryan Gosling"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F005",
                "title": "Future World 2099",
                "poster_url": "https://via.placeholder.com/300x450?text=Future+World",
                "language": "English",
                "duration_min": 135,
                "rating": "PG-13",
                "release_date": date.today() + timedelta(days=7),
                "description": "A dystopian future where humanity fights for survival",
                "director": "Denis Villeneuve",
                "trailer_url": "https://youtube.com/watch?v=example5",
                "genre_names": ["Sci-Fi", "Action"],
                "cast": ["Timothée Chalamet", "Zendaya", "Oscar Isaac"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F006",
                "title": "The Family Secret",
                "poster_url": "https://via.placeholder.com/300x450?text=Family+Secret",
                "language": "English",
                "duration_min": 118,
                "rating": "PG-13",
                "release_date": date.today() - timedelta(days=2),
                "description": "A gripping drama about family, secrets, and redemption",
                "director": "Greta Gerwig",
                "trailer_url": "https://youtube.com/watch?v=example6",
                "genre_names": ["Drama"],
                "cast": ["Saoirse Ronan", "Laura Dern", "Florence Pugh"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F007",
                "title": "Bangla Bhalobasha",
                "poster_url": "https://via.placeholder.com/300x450?text=Bangla+Bhalobasha",
                "language": "Bangla",
                "duration_min": 125,
                "rating": "PG",
                "release_date": date.today() - timedelta(days=10),
                "description": "A beautiful Bengali love story",
                "director": "Anik Dutta",
                "trailer_url": "https://youtube.com/watch?v=example7",
                "genre_names": ["Romance", "Drama"],
                "cast": ["Jaya Ahsan", "Chanchal Chowdhury"]
            },
            {
                "eidr": "10.5240/AAAA-BBBB-CCCC-DDDD-EEEE-F008",
                "title": "Space Odyssey",
                "poster_url": "https://via.placeholder.com/300x450?text=Space+Odyssey",
                "language": "English",
                "duration_min": 160,
                "rating": "PG-13",
                "release_date": date.today() + timedelta(days=14),
                "description": "An epic journey through space and time",
                "director": "Christopher Nolan",
                "trailer_url": "https://youtube.com/watch?v=example8",
                "genre_names": ["Sci-Fi", "Adventure"],
                "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"]
            },
        ]

        movies = []
        for movie_data in movies_data:
            genre_names = movie_data.pop("genre_names")
            cast_members = movie_data.pop("cast")

            movie = Movie(**movie_data)
            movie.genres = [g for g in genres if g.name in genre_names]
            db.add(movie)
            db.flush()

            for cast_member in cast_members:
                db.execute(
                    movie_cast_association.insert().values(
                        movie_eidr=movie.eidr,
                        cast_member=cast_member
                    )
                )
            movies.append(movie)

        print(f"Created {len(movies)} movies")

        # Create sample reviews
        print("\nCreating sample reviews...")
        review_texts = [
            "Amazing movie! Highly recommended.",
            "Great story and excellent performances.",
            "One of the best movies I've seen this year.",
            "Loved every minute of it!",
            "Good movie but could have been better.",
            "Interesting plot with some surprising twists.",
            "The cinematography was breathtaking.",
            "A must-watch for fans of the genre."
        ]

        reviews_created = 0
        for movie in movies[:5]:
            num_reviews = random.randint(2, 5)
            for i in range(num_reviews):
                review = Review(
                    movie_eidr=movie.eidr,
                    user_id=f"user_{reviews_created + 1}",
                    rating=round(random.uniform(3.0, 5.0), 1),
                    review_text=random.choice(review_texts)
                )
                db.add(review)
                reviews_created += 1

        print(f"Created {reviews_created} sample reviews")

        db.commit()
        print("\nDatabase initialization completed successfully!")

        print("\n" + "=" * 50)
        print("DATABASE SUMMARY")
        print("=" * 50)
        print(f"Genres : {db.query(Genre).count()}")
        print(f"Movies : {db.query(Movie).count()}")
        print(f"Reviews: {db.query(Review).count()}")
        print("=" * 50)

    except Exception as e:
        print(f"\nError during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()