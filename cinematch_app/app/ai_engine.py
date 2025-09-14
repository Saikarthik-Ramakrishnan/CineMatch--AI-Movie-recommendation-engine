import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sentence_transformers import SentenceTransformer
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import json
import os
import requests
from datetime import datetime
import random
class MovieRecommendationEngine:
    def __init__(self):
        self.movies_df = None
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.load_movie_data()
        self.prepare_recommendation_models()
    
    def load_movie_data(self):
        """Load movie data from JSON file or create sample data"""
        try:
            with open('data/movies.json', 'r') as f:
                movies_data = json.load(f)
            self.movies_df = pd.DataFrame(movies_data)
        except FileNotFoundError:
            # Create sample movie data if file doesn't exist
            self.create_sample_movie_data()
    
    def create_sample_movie_data(self):
        """Create sample movie dataset"""
        sample_movies = [
            {
                "id": 1,
                "title": "Inception",
                "genres": ["Sci-Fi", "Thriller", "Action"],
                "year": 2010,
                "director": "Christopher Nolan",
                "plot": "A thief who steals corporate secrets through dream-sharing technology",
                "rating": 8.8,
                "runtime": 148,
                "mood_tags": ["mind-bending", "complex", "visually-stunning"],
                "context_tags": ["date-night", "mind-bender"],
                "poster_url": "/static/images/inception.jpg"
            },
            {
                "id": 2,
                "title": "The Grand Budapest Hotel",
                "genres": ["Comedy", "Drama"],
                "year": 2014,
                "director": "Wes Anderson",
                "plot": "The adventures of Gustave H, legendary concierge at famous European hotel",
                "rating": 8.1,
                "runtime": 99,
                "mood_tags": ["whimsical", "colorful", "charming"],
                "context_tags": ["cozy", "date-night"],
                "poster_url": "/static/images/budapest.jpg"
            },
            {
                "id": 3,
                "title": "Parasite",
                "genres": ["Thriller", "Drama", "Comedy"],
                "year": 2019,
                "director": "Bong Joon-ho",
                "plot": "Greed and class discrimination threaten the newly formed symbiotic relationship",
                "rating": 8.6,
                "runtime": 132,
                "mood_tags": ["thought-provoking", "intense", "acclaimed"],
                "context_tags": ["mind-bender", "serious"],
                "poster_url": "/static/images/parasite.jpg"
            },
            {
                "id": 4,
                "title": "Paddington 2",
                "genres": ["Family", "Comedy", "Adventure"],
                "year": 2017,
                "director": "Paul King",
                "plot": "Paddington, now settled with the Brown family, picks up a series of odd jobs",
                "rating": 8.2,
                "runtime": 103,
                "mood_tags": ["heartwarming", "wholesome", "feel-good"],
                "context_tags": ["family", "cozy"],
                "poster_url": "/static/images/paddington.jpg"
            },
            {
                "id": 5,
                "title": "Mad Max: Fury Road",
                "genres": ["Action", "Adventure", "Sci-Fi"],
                "year": 2015,
                "director": "George Miller",
                "plot": "In a post-apocalyptic wasteland, Max teams up with Furiosa",
                "rating": 8.1,
                "runtime": 120,
                "mood_tags": ["intense", "adrenaline", "spectacular"],
                "context_tags": ["friday-night", "action"],
                "poster_url": "/static/images/madmax.jpg"
            }
        ]
        
        # Add more movies to reach a good dataset size
        for i in range(6, 51):
            sample_movies.append({
                "id": i,
                "title": f"Sample Movie {i}",
                "genres": random.choice([["Drama"], ["Comedy"], ["Action"], ["Sci-Fi", "Drama"]]),
                "year": random.randint(2010, 2023),
                "director": f"Director {i}",
                "plot": f"An engaging story about {random.choice(['love', 'adventure', 'mystery', 'discovery'])}",
                "rating": round(random.uniform(6.0, 9.0), 1),
                "runtime": random.randint(90, 180),
                "mood_tags": random.sample(["exciting", "emotional", "funny", "intense", "uplifting"], 2),
                "context_tags": random.sample(["family", "date-night", "friday-night", "cozy"], 2),
                "poster_url": f"/static/images/movie{i}.jpg"
            })
        
        self.movies_df = pd.DataFrame(sample_movies)
        
        # Save to file
        os.makedirs('data', exist_ok=True)
        with open('data/movies.json', 'w') as f:
            json.dump(sample_movies, f, indent=2)
    
    def prepare_recommendation_models(self):
        """Prepare ML models for recommendations"""
        # Create feature matrix for content-based filtering
        self.movies_df['combined_features'] = (
            self.movies_df['plot'] + ' ' +
            self.movies_df['genres'].apply(lambda x: ' '.join(x)) + ' ' +
            self.movies_df['mood_tags'].apply(lambda x: ' '.join(x))
        )
        
        # TF-IDF Vectorization
        tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
        self.tfidf_matrix = tfidf.fit_transform(self.movies_df['combined_features'])
        
        # Compute cosine similarity
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
    
    def get_contextual_recommendations(self, context, limit=6):
        """Get recommendations based on context"""
        context_movies = self.movies_df[
            self.movies_df['context_tags'].apply(lambda x: context in x)
        ]
        
        if len(context_movies) < limit:
            # If not enough context-specific movies, add similar ones
            additional_movies = self.movies_df[
                ~self.movies_df['id'].isin(context_movies['id'])
            ].sample(n=limit-len(context_movies))
            context_movies = pd.concat([context_movies, additional_movies])
        
        return self.format_recommendations(context_movies.head(limit))
    
    def get_chat_recommendations(self, user_message, limit=6):
        """Analyze user message and return recommendations"""
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.polarity_scores(user_message)
        
        # Extract keywords and preferences
        message_lower = user_message.lower()
        
        # Genre detection
        genre_keywords = {
            'action': ['action', 'fight', 'explosion', 'adrenaline'],
            'comedy': ['funny', 'laugh', 'humor', 'comedy'],
            'drama': ['emotional', 'deep', 'serious', 'drama'],
            'sci-fi': ['sci-fi', 'science', 'future', 'space'],
            'thriller': ['thriller', 'suspense', 'mystery', 'tension'],
            'romance': ['love', 'romantic', 'relationship', 'romance']
        }
        
        detected_genres = []
        for genre, keywords in genre_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_genres.append(genre.title())
        
        # Mood detection
        if sentiment['compound'] > 0.3:
            mood_preference = 'positive'
        elif sentiment['compound'] < -0.3:
            mood_preference = 'negative'
        else:
            mood_preference = 'neutral'
        
        # Filter movies based on analysis
        filtered_movies = self.movies_df.copy()
        
        if detected_genres:
            filtered_movies = filtered_movies[
                filtered_movies['genres'].apply(
                    lambda x: any(genre in x for genre in detected_genres)
                )
            ]
        
        # Use semantic similarity for more sophisticated matching
        if len(filtered_movies) > limit:
            movie_embeddings = self.sentence_model.encode(
                filtered_movies['combined_features'].tolist()
            )
            query_embedding = self.sentence_model.encode([user_message])
            
            similarities = cosine_similarity(query_embedding, movie_embeddings)[0]
            filtered_movies['similarity'] = similarities
            filtered_movies = filtered_movies.sort_values('similarity', ascending=False)
        
        return self.format_recommendations(filtered_movies.head(limit))
    
    def get_similar_movies(self, movie_id, limit=6):
        """Get movies similar to a specific movie"""
        try:
            movie_idx = self.movies_df[self.movies_df['id'] == movie_id].index[0]
            similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            
            # Get indices of most similar movies (excluding the movie itself)
            similar_indices = [i[0] for i in similarity_scores[1:limit+1]]
            similar_movies = self.movies_df.iloc[similar_indices]
            
            return self.format_recommendations(similar_movies)
        except IndexError:
            return self.get_random_recommendations(limit)
    
    def get_random_recommendations(self, limit=6):
        """Get random movie recommendations"""
        random_movies = self.movies_df.sample(n=min(limit, len(self.movies_df)))
        return self.format_recommendations(random_movies)
    
    def format_recommendations(self, movies_df):
        """Format movies for frontend consumption"""
        recommendations = []
        for _, movie in movies_df.iterrows():
            # Calculate match percentage (simplified)
            match_score = min(95, max(75, movie['rating'] * 10 + random.randint(-5, 5)))
            
            recommendations.append({
                'id': movie['id'],
                'title': movie['title'],
                'genres': ' • '.join(movie['genres']),
                'year': movie['year'],
                'rating': movie['rating'],
                'runtime': movie['runtime'],
                'director': movie['director'],
                'plot': movie['plot'],
                'match': f"{match_score}%",
                'explanation': self.generate_explanation(movie),
                'poster_url': movie['poster_url']
            })
        
        return recommendations
    
    def generate_explanation(self, movie):
        """Generate explanation for why movie was recommended"""
        explanations = [
            f"Highly rated {movie['genres'][0].lower()} with stellar reviews",
            f"Perfect {movie['runtime']}-minute runtime for your mood",
            f"Acclaimed {movie['year']} film by {movie['director']}",
            f"Combines {' and '.join(movie['genres'][:2]).lower()} elements beautifully",
            f"Features {', '.join(movie['mood_tags'][:2])} storytelling"
        ]
        return random.choice(explanations)

# Initialize global recommendation engine
recommendation_engine = MovieRecommendationEngine()