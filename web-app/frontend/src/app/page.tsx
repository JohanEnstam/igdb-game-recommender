"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Star, Calendar, Gamepad2 } from "lucide-react";

interface Game {
  id: number;
  name: string;
  summary: string;
  rating: number;
  first_release_date: string;
  cover_url: string;
}

interface RecommendationResponse {
  game_id: number;
  recommended_games: Game[];
}

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Game[]>([]);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [recommendations, setRecommendations] = useState<Game[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use environment variable for API URL (will be set in Cloud Run)
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://igdb-recommendation-api-dev-5wxthq523q-ew.a.run.app";

  const searchGames = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError(null);
    
    const searchUrl = `${API_BASE_URL}/games/search?query=${encodeURIComponent(searchQuery)}&limit=3`;
    console.log("🔍 Searching games with URL:", searchUrl);
    console.log("🌐 API_BASE_URL:", API_BASE_URL);
    
    try {
          const response = await fetch(searchUrl, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            mode: 'cors',
            credentials: 'include'
          });
      console.log("📡 Response status:", response.status);
      console.log("📡 Response headers:", Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        throw new Error(`Failed to search games: ${response.status} ${response.statusText}`);
      }
      const games = await response.json();
      console.log("🎮 Found games:", games.length);
      setSearchResults(games);
      
      if (games.length === 0) {
        setError("No games found. Try a different search term.");
      }
    } catch (err) {
      console.error("❌ Search error:", err);
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getRecommendations = async (gameId: number) => {
    setLoading(true);
    setError(null);
    
    const recUrl = `${API_BASE_URL}/recommendations/${gameId}?limit=5`;
    console.log("🎯 Getting recommendations with URL:", recUrl);
    
    try {
      const response = await fetch(recUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        credentials: 'include'
      });
      console.log("📡 Recommendations response status:", response.status);
      
      if (!response.ok) {
        throw new Error(`Failed to get recommendations: ${response.status} ${response.statusText}`);
      }
      const data: RecommendationResponse = await response.json();
      console.log("🎮 Found recommendations:", data.recommended_games.length);
      setRecommendations(data.recommended_games);
    } catch (err) {
      console.error("❌ Recommendations error:", err);
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleGameSelect = (game: Game) => {
    setSelectedGame(game);
    getRecommendations(game.id);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      searchGames();
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Gamepad2 className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold text-foreground">
              IGDB Game Recommender
            </h1>
          </div>
          <p className="text-lg text-muted-foreground">
            Discover new games based on your favorites
          </p>
        </div>

        {/* Search Section */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="flex gap-2">
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Search for a game..."
              className="flex-1"
            />
            <Button
              onClick={searchGames}
              disabled={loading || !searchQuery.trim()}
              className="px-6"
            >
              <Search className="h-4 w-4 mr-2" />
              {loading ? "Searching..." : "Search"}
            </Button>
          </div>
        </div>

        {/* Debug Info */}
        <div className="max-w-2xl mx-auto mb-8 p-4 bg-muted/50 border border-muted rounded-lg">
          <h3 className="text-sm font-semibold mb-2">🔧 Debug Info</h3>
          <p className="text-xs text-muted-foreground">
            <strong>API URL:</strong> {API_BASE_URL}
          </p>
          <p className="text-xs text-muted-foreground">
            <strong>Environment:</strong> {process.env.NODE_ENV || 'development'}
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8 p-4 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg">
            <h3 className="font-semibold mb-2">❌ Error</h3>
            {error}
          </div>
        )}

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-semibold text-foreground mb-6">Search Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {searchResults.map((game) => (
                <Card
                  key={game.id}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    selectedGame?.id === game.id
                      ? "ring-2 ring-primary bg-primary/5"
                      : "hover:bg-muted/50"
                  }`}
                  onClick={() => handleGameSelect(game)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start gap-3">
                      {game.cover_url && (
                        <img
                          src={game.cover_url}
                          alt={game.name}
                          className="w-16 h-20 object-cover rounded"
                        />
                      )}
                      <div className="flex-1">
                        <CardTitle className="text-lg">{game.name}</CardTitle>
                        <div className="flex items-center gap-2 mt-2">
                          {game.rating && (
                            <Badge variant="secondary" className="text-xs">
                              <Star className="h-3 w-3 mr-1" />
                              {game.rating.toFixed(1)}
                            </Badge>
                          )}
                          {game.first_release_date && (
                            <Badge variant="outline" className="text-xs">
                              <Calendar className="h-3 w-3 mr-1" />
                              {new Date(game.first_release_date).getFullYear()}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm">
                      {game.summary?.substring(0, 120)}...
                    </CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Selected Game and Recommendations */}
        {selectedGame && (
          <div>
            {/* Selected Game */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="text-2xl">Selected Game</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-start gap-4">
                  {selectedGame.cover_url && (
                    <img
                      src={selectedGame.cover_url}
                      alt={selectedGame.name}
                      className="w-24 h-32 object-cover rounded"
                    />
                  )}
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold mb-2">{selectedGame.name}</h3>
                    <p className="text-muted-foreground mb-3">{selectedGame.summary}</p>
                    <div className="flex items-center gap-4">
                      {selectedGame.rating && (
                        <Badge variant="secondary">
                          <Star className="h-4 w-4 mr-1" />
                          Rating: {selectedGame.rating.toFixed(1)}
                        </Badge>
                      )}
                      {selectedGame.first_release_date && (
                        <Badge variant="outline">
                          <Calendar className="h-4 w-4 mr-1" />
                          Released: {new Date(selectedGame.first_release_date).getFullYear()}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommendations */}
            <div>
              <h2 className="text-2xl font-semibold text-foreground mb-6">Recommended Games</h2>
              {loading ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <p className="mt-2 text-muted-foreground">Finding recommendations...</p>
                </div>
              ) : recommendations.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {recommendations.map((game) => (
                    <Card key={game.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        {game.cover_url && (
                          <img
                            src={game.cover_url}
                            alt={game.name}
                            className="w-full h-48 object-cover rounded mb-3"
                          />
                        )}
                        <h3 className="font-semibold mb-2">{game.name}</h3>
                        <p className="text-sm text-muted-foreground mb-3">
                          {game.summary?.substring(0, 80)}...
                        </p>
                        <div className="flex items-center gap-2">
                          {game.rating && (
                            <Badge variant="secondary" className="text-xs">
                              <Star className="h-3 w-3 mr-1" />
                              {game.rating.toFixed(1)}
                            </Badge>
                          )}
                          {game.first_release_date && (
                            <Badge variant="outline" className="text-xs">
                              <Calendar className="h-3 w-3 mr-1" />
                              {new Date(game.first_release_date).getFullYear()}
                            </Badge>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No recommendations found for this game.
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}