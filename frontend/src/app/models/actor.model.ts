export interface Movie {
  id: number;
  title: string;
}

export interface Actor {
  id?: number;
  name: string;
  birth_date: string;
  age?: number;
  gender: string;
  movies?: Movie[];
}

export interface ActorResponse {
  success: boolean;
  actor?: Actor;
  actors?: Actor[];
  total_actors?: number;
  created?: number;
  deleted?: number;
  message?: string;
  actor_id?: number;
  actor_name?: string;
  movies?: any[];
  total_movies?: number;
}