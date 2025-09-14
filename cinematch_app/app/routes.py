import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from flask import Blueprint, jsonify, request
from ai_engine import recommendation_engine

import json

main = Blueprint('main', __name__)

@main.route('/')
def home():
   return render_template('index.html')
#def index():
 #   return jsonify({"message": "CineMatch API is running!"})

@main.route('/api/recommendations/context/<context>')
def get_contextual_recommendations(context):
    """Get recommendations based on context (e.g., 'friday-night', 'cozy')"""
    try:
        recommendations = recommendation_engine.get_contextual_recommendations(context)
        return jsonify({
            "success": True,
            "context": context,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main.route('/api/recommendations/chat', methods=['POST'])
def get_chat_recommendations():
    """Get recommendations based on user chat message"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"success": False, "error": "Message is required"}), 400
        
        recommendations = recommendation_engine.get_chat_recommendations(message)
        
        # Generate AI response
        ai_responses = {
            'funny': "Great choice! I found some fantastic comedies that'll have you laughing out loud.",
            'scary': "Perfect! Here are some spine-chilling movies that'll keep you on the edge of your seat.",
            'inception': "Ah, a fellow mind-bender enthusiast! These films will twist your perception of reality.",
            'default': "Excellent taste! Based on your message, here are some perfectly matched recommendations."
        }
        
        message_lower = message.lower()
        ai_response = ai_responses.get('default')
        for key, response in ai_responses.items():
            if key in message_lower:
                ai_response = response
                break
        
        return jsonify({
            "success": True,
            "ai_response": ai_response,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main.route('/api/recommendations/similar/<int:movie_id>')
def get_similar_recommendations(movie_id):
    """Get movies similar to a specific movie"""
    try:
        recommendations = recommendation_engine.get_similar_movies(movie_id)
        return jsonify({
            "success": True,
            "movie_id": movie_id,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main.route('/api/movies')
def get_all_movies():
    """Get all movies in database"""
    try:
        movies = recommendation_engine.movies_df.to_dict('records')
        return jsonify({
            "success": True,
            "movies": movies,
            "total": len(movies)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main.route('/api/movies/<int:movie_id>')
def get_movie_details(movie_id):
    """Get detailed information about a specific movie"""
    try:
        movie = recommendation_engine.movies_df[
            recommendation_engine.movies_df['id'] == movie_id
        ]
        
        if movie.empty:
            return jsonify({"success": False, "error": "Movie not found"}), 404
        
        movie_data = movie.iloc[0].to_dict()
        return jsonify({
            "success": True,
            "movie": movie_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main.route('/api/search')
def search_movies():
    """Search movies by title, genre, or director"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({"success": False, "error": "Search query is required"}), 400
        
        movies_df = recommendation_engine.movies_df
        
        # Search in title, genres, and director
        results = movies_df[
            movies_df['title'].str.lower().str.contains(query) |
            movies_df['director'].str.lower().str.contains(query) |
            movies_df['genres'].apply(lambda x: any(query in genre.lower() for genre in x))
        ]
        
        formatted_results = recommendation_engine.format_recommendations(results)
        
        return jsonify({
            "success": True,
            "query": query,
            "results": formatted_results,
            "total": len(formatted_results)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@main.route('/api/genres')
def get_genres():
    """Get all available genres"""
    try:
        all_genres = set()
        for genres_list in recommendation_engine.movies_df['genres']:
            all_genres.update(genres_list)
        
        return jsonify({
            "success": True,
            "genres": sorted(list(all_genres))
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
