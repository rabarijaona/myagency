import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Movie, MovieResponse } from '../models/movie.model';
import { Actor, ActorResponse } from '../models/actor.model';
import { User, UserResponse, RoleResponse } from '../models/user.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  getMovies(): Observable<MovieResponse> {
    return this.http.get<MovieResponse>(`${this.apiUrl}/movies`);
  }

  getMovie(id: number): Observable<MovieResponse> {
    return this.http.get<MovieResponse>(`${this.apiUrl}/movies/${id}`);
  }

  createMovie(movie: Movie): Observable<MovieResponse> {
    return this.http.post<MovieResponse>(
      `${this.apiUrl}/movies`,
      movie,
      { headers: this.getHeaders() }
    );
  }

  updateMovie(id: number, movie: Partial<Movie>): Observable<MovieResponse> {
    return this.http.patch<MovieResponse>(
      `${this.apiUrl}/movies/${id}`,
      movie,
      { headers: this.getHeaders() }
    );
  }

  deleteMovie(id: number): Observable<MovieResponse> {
    return this.http.delete<MovieResponse>(`${this.apiUrl}/movies/${id}`);
  }

  getActors(): Observable<ActorResponse> {
    return this.http.get<ActorResponse>(`${this.apiUrl}/actors`);
  }

  getActor(id: number): Observable<ActorResponse> {
    return this.http.get<ActorResponse>(`${this.apiUrl}/actors/${id}`);
  }

  createActor(actor: Actor): Observable<ActorResponse> {
    return this.http.post<ActorResponse>(
      `${this.apiUrl}/actors`,
      actor,
      { headers: this.getHeaders() }
    );
  }

  updateActor(id: number, actor: Partial<Actor>): Observable<ActorResponse> {
    return this.http.patch<ActorResponse>(
      `${this.apiUrl}/actors/${id}`,
      actor,
      { headers: this.getHeaders() }
    );
  }

  deleteActor(id: number): Observable<ActorResponse> {
    return this.http.delete<ActorResponse>(`${this.apiUrl}/actors/${id}`);
  }

  getMovieWithActors(id: number): Observable<MovieResponse> {
    return this.http.get<MovieResponse>(`${this.apiUrl}/movies/${id}?include_actors=true`);
  }

  getActorWithMovies(id: number): Observable<ActorResponse> {
    return this.http.get<ActorResponse>(`${this.apiUrl}/actors/${id}?include_movies=true`);
  }

  getMovieActors(movieId: number): Observable<MovieResponse> {
    return this.http.get<MovieResponse>(`${this.apiUrl}/movies/${movieId}/actors`);
  }

  getActorMovies(actorId: number): Observable<ActorResponse> {
    return this.http.get<ActorResponse>(`${this.apiUrl}/actors/${actorId}/movies`);
  }

  assignActorToMovie(movieId: number, actorId: number): Observable<MovieResponse> {
    return this.http.post<MovieResponse>(
      `${this.apiUrl}/movies/${movieId}/actors/${actorId}`,
      {},
      { headers: this.getHeaders() }
    );
  }

  removeActorFromMovie(movieId: number, actorId: number): Observable<MovieResponse> {
    return this.http.delete<MovieResponse>(`${this.apiUrl}/movies/${movieId}/actors/${actorId}`);
  }

  getUsers(page: number = 0, perPage: number = 50, search?: string): Observable<UserResponse> {
    let url = `${this.apiUrl}/users?page=${page}&per_page=${perPage}`;
    if (search) {
      url += `&search=${encodeURIComponent(search)}`;
    }
    return this.http.get<UserResponse>(url);
  }

  getUser(userId: string): Observable<UserResponse> {
    return this.http.get<UserResponse>(`${this.apiUrl}/users/${userId}`);
  }

  createUser(user: { email: string; password: string; name?: string; role?: string }): Observable<UserResponse> {
    return this.http.post<UserResponse>(
      `${this.apiUrl}/users`,
      user,
      { headers: this.getHeaders() }
    );
  }

  updateUser(userId: string, updates: Partial<User>): Observable<UserResponse> {
    return this.http.patch<UserResponse>(
      `${this.apiUrl}/users/${userId}`,
      updates,
      { headers: this.getHeaders() }
    );
  }

  deleteUser(userId: string): Observable<UserResponse> {
    return this.http.delete<UserResponse>(`${this.apiUrl}/users/${userId}`);
  }

  getUserRoles(userId: string): Observable<RoleResponse> {
    return this.http.get<RoleResponse>(`${this.apiUrl}/users/${userId}/roles`);
  }

  assignUserRoles(userId: string, roleIds: string[]): Observable<UserResponse> {
    return this.http.post<UserResponse>(
      `${this.apiUrl}/users/${userId}/roles`,
      { roles: roleIds },
      { headers: this.getHeaders() }
    );
  }

  getAllRoles(): Observable<RoleResponse> {
    return this.http.get<RoleResponse>(`${this.apiUrl}/roles`);
  }
}