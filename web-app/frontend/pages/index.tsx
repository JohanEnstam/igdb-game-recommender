import React, { useState } from 'react';
import Head from 'next/head';
import { TextField, Button, Card, CardContent, CardMedia, Typography, Grid, Container, Box, CircularProgress } from '@mui/material';
import axios from 'axios';

// Define types
interface Game {
  id: number;
  name: string;
  summary?: string;
  rating?: number;
  first_release_date?: string;
  cover_url?: string;
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Game[]>([]);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [recommendations, setRecommendations] = useState<Game[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // API base URL from environment variable or default to localhost
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError('');
    setSearchResults([]);
    setSelectedGame(null);
    setRecommendations([]);

    try {
      const response = await axios.get(`${API_URL}/games/search?query=${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data);
    } catch (err) {
      console.error('Error searching games:', err);
      setError('Failed to search games. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectGame = async (game: Game) => {
    setLoading(true);
    setError('');
    setSelectedGame(game);
    setRecommendations([]);

    try {
      const response = await axios.get(`${API_URL}/recommendations/${game.id}`);
      setRecommendations(response.data.recommended_games);
    } catch (err) {
      console.error('Error getting recommendations:', err);
      setError('Failed to get recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <Container maxWidth="lg">
      <Head>
        <title>IGDB Game Recommender</title>
        <meta name="description" content="Find your next favorite game" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Box sx={{ my: 4, textAlign: 'center' }}>
        <Typography variant="h2" component="h1" gutterBottom>
          IGDB Game Recommender
        </Typography>
        <Typography variant="h5" component="h2" color="text.secondary" gutterBottom>
          Find your next favorite game
        </Typography>

        <Box component="form" onSubmit={handleSearch} sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <TextField
            label="Search for a game"
            variant="outlined"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ width: '50%', minWidth: '300px' }}
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary" 
            sx={{ ml: 2 }}
            disabled={loading}
          >
            Search
          </Button>
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        {searchResults.length > 0 && !selectedGame && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
              Search Results
            </Typography>
            <Grid container spacing={3}>
              {searchResults.map((game) => (
                <Grid item xs={12} sm={6} md={4} key={game.id}>
                  <Card 
                    sx={{ 
                      height: '100%', 
                      display: 'flex', 
                      flexDirection: 'column',
                      cursor: 'pointer',
                      '&:hover': {
                        boxShadow: 6
                      }
                    }}
                    onClick={() => handleSelectGame(game)}
                  >
                    <CardMedia
                      component="img"
                      height="200"
                      image={game.cover_url || '/placeholder-game.jpg'}
                      alt={game.name}
                      sx={{ objectFit: 'contain', p: 1 }}
                    />
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography gutterBottom variant="h6" component="div">
                        {game.name}
                      </Typography>
                      {game.rating && (
                        <Typography variant="body2" color="text.secondary">
                          Rating: {game.rating.toFixed(1)}/10
                        </Typography>
                      )}
                      <Typography variant="body2" color="text.secondary">
                        Released: {formatDate(game.first_release_date)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {selectedGame && (
          <Box sx={{ mt: 4 }}>
            <Button 
              variant="outlined" 
              onClick={() => setSelectedGame(null)}
              sx={{ mb: 2 }}
            >
              Back to Search Results
            </Button>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardMedia
                    component="img"
                    height="300"
                    image={selectedGame.cover_url || '/placeholder-game.jpg'}
                    alt={selectedGame.name}
                    sx={{ objectFit: 'contain', p: 1 }}
                  />
                  <CardContent>
                    <Typography gutterBottom variant="h5" component="div">
                      {selectedGame.name}
                    </Typography>
                    {selectedGame.rating && (
                      <Typography variant="body1">
                        Rating: {selectedGame.rating.toFixed(1)}/10
                      </Typography>
                    )}
                    <Typography variant="body2" color="text.secondary">
                      Released: {formatDate(selectedGame.first_release_date)}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 2 }}>
                      {selectedGame.summary}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={8}>
                <Typography variant="h5" gutterBottom>
                  Recommendations
                </Typography>
                
                {recommendations.length > 0 ? (
                  <Grid container spacing={2}>
                    {recommendations.map((game) => (
                      <Grid item xs={12} sm={6} key={game.id}>
                        <Card sx={{ 
                          display: 'flex', 
                          height: '100%',
                          cursor: 'pointer',
                          '&:hover': {
                            boxShadow: 6
                          }
                        }}
                        onClick={() => handleSelectGame(game)}
                        >
                          <CardMedia
                            component="img"
                            sx={{ width: 100, objectFit: 'contain', p: 1 }}
                            image={game.cover_url || '/placeholder-game.jpg'}
                            alt={game.name}
                          />
                          <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                            <CardContent sx={{ flex: '1 0 auto' }}>
                              <Typography component="div" variant="h6">
                                {game.name}
                              </Typography>
                              {game.rating && (
                                <Typography variant="body2" color="text.secondary">
                                  Rating: {game.rating.toFixed(1)}/10
                                </Typography>
                              )}
                              <Typography variant="body2" color="text.secondary" noWrap>
                                {game.summary?.substring(0, 60)}
                                {game.summary && game.summary.length > 60 ? '...' : ''}
                              </Typography>
                            </CardContent>
                          </Box>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Typography>No recommendations found.</Typography>
                )}
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>
    </Container>
  );
}
