export interface Actor {
  id: number;
  name: string;
}

export interface Movie {
  id?: number;
  title: string;
  release_date: string;
  actors?: Actor[];
}

export interface MovieResponse {
  success: boolean;
  movie?: Movie;
  movies?: Movie[];
  total_movies?: number;
  created?: number;
  deleted?: number;
  message?: string;
  movie_id?: number;
  movie_title?: string;
  actors?: any[];
  total_actors?: number;
}