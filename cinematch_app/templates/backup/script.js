
// API Configuration

const API_BASE_URL = 'http://localhost:5000/api';

const userPreferences = {};

// Updated function to connect with backend
async function selectContext(context) {
    userPreferences.context = context;
    
    // Highlight selected card
    document.querySelectorAll('.context-card').forEach(card => {
        card.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    });
    event.currentTarget.style.borderColor = 'rgba(102, 126, 234, 0.5)';
    
    // Show loading state
    showRecommendationLoading();
    
    try {
        // Call backend API
        const response = await fetch(`${API_BASE_URL}/recommendations/context/${context}`);
        const data = await response.json();
        
        if (data.success) {
            displayRecommendations(data.recommendations, 'homeRecommendations');
        } else {
            console.error('API Error:', data.error);
            generateContextualRecommendations(context); // Fallback
        }
    } catch (error) {
        console.error('Network error:', error);
        generateContextualRecommendations(context); // Fallback
    }
}

// Updated chat function
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addChatMessage(message, 'user');
    
    // Clear input
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Call backend API
        const response = await fetch(`${API_BASE_URL}/recommendations/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        removeTypingIndicator();
        
        if (data.success) {
            addChatMessage(data.ai_response, 'ai');
            displayRecommendations(data.recommendations, 'homeRecommendations');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    } catch (error) {
        console.error('Network error:', error);
        removeTypingIndicator();
        addChatMessage('Network error. Please check your connection.', 'ai');
    }
}

// Movie search function
async function searchMovies(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            return data.results;
        }
        return [];
    } catch (error) {
        console.error('Search error:', error);
        return [];
    }
}

// Get movie details
async function getMovieDetails(movieId) {
    try {
        const response = await fetch(`${API_BASE_URL}/movies/${movieId}`);
        const data = await response.json();
        
        if (data.success) {
            return data.movie;
        }
        return null;
    } catch (error) {
        console.error('Error fetching movie details:', error);
        return null;
    }
}



function addChatMessage(message, sender) {
    console.log(`Message from ${sender}:`, message);
    // TODO: Display message in chat UI
}

function displayRecommendations(data, containerId) {
    console.log("Displaying recommendations in", containerId, data);
    // TODO: Populate DOM with movie cards
}

function generateContextualRecommendations(context) {
    console.log("Generating fallback recommendations for context:", context);
    // TODO: Implement fallback logic
}

function showRecommendationLoading() {
    console.log("Loading recommendations...");
    // TODO: Show loading skeleton or indicator
}

function showTypingIndicator() {
    console.log("Showing typing indicator...");
    // TODO: Show bot typing animation
}

function removeTypingIndicator() {
    console.log("Removing typing indicator...");
    // TODO: Hide typing animation
}
