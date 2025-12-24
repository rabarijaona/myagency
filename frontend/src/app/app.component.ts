import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './services/api.service';
import { PermissionService } from './services/permission.service';
import { AuthService } from '@auth0/auth0-angular';
import { Movie } from './models/movie.model';
import { Actor } from './models/actor.model';
import { User, Role } from './models/user.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'Casting Agency Management';
  activeTab: 'movies' | 'actors' | 'casting' | 'users' = 'movies';
  Math = Math
  // Movies
  movies: Movie[] = [];
  selectedMovie: Movie | null = null;
  movieForm: Movie = { title: '', release_date: '' };
  isEditingMovie = false;

  // Actors
  actors: Actor[] = [];
  selectedActor: Actor | null = null;
  actorForm: Actor = { name: '', birth_date: '', gender: '' };
  isEditingActor = false;

  // Casting
  selectedMovieForCasting: Movie | null = null;
  selectedActorForCasting: Actor | null = null;
  movieActors: any[] = [];
  actorMovies: any[] = [];
  availableActors: Actor[] = [];

  // Users
  users: User[] = [];
  selectedUser: User | null = null;
  userForm: { email: string; password: string; name: string; role: string } = {
    email: '',
    password: '',
    name: '',
    role: 'Casting Assistant'
  };
  isEditingUser = false;
  availableRoles: Role[] = [];
  selectedUserRoles: Role[] = [];
  searchQuery = '';
  currentPage = 0;
  totalUsers = 0;
  perPage = 50;

  // UI State
  loading = false;
  error: string | null = null;
  success: string | null = null;

  // Authentication State
  isAuthenticated = false;

  constructor(
    private apiService: ApiService,
    public permissions: PermissionService,
    public auth: AuthService
  ) {}

  ngOnInit() {
    this.loadMovies();
    this.loadActors();

    // Subscribe to authentication state
    this.auth.isAuthenticated$.subscribe(isAuth => {
      this.isAuthenticated = isAuth;
    });

    // Subscribe to user data and extract permissions from token
    this.auth.user$.subscribe(user => {
      console.log('Auth0 user changed:', user);
      if (user) {
        // Get the ID token claims which contain the permissions
        this.auth.idTokenClaims$.subscribe(claims => {
          console.log('=== Auth0 ID Token Claims ===');
          console.log('ID Token Claims object:', claims);
          console.log('ID Token Claims (formatted):', JSON.stringify(claims, null, 2));

          if (claims) {
            // Try to extract permissions from ID token
            this.permissions.setPermissionsFromToken(claims);
          }
        });

        // Also try to get access token claims (permissions are often here)
        this.auth.getAccessTokenSilently().subscribe({
          next: (token) => {
            console.log('=== Access Token ===');
            console.log('Access token obtained:', token ? 'Yes' : 'No');

            // Decode the access token to see its claims
            if (token) {
              try {
                const parts = token.split('.');
                if (parts.length === 3) {
                  const payload = JSON.parse(atob(parts[1]));
                  console.log('Access Token Claims:', payload);
                  console.log('Access Token Claims (formatted):', JSON.stringify(payload, null, 2));

                  // If ID token didn't have permissions, try access token
                  this.auth.idTokenClaims$.subscribe(idClaims => {
                    if (idClaims && (!idClaims['permissions'] && !Object.keys(idClaims).some(k => k.includes('permissions')))) {
                      console.log('No permissions in ID token, trying access token...');
                      this.permissions.setPermissionsFromToken(payload);
                    }
                  });
                }
              } catch (e) {
                console.error('Error decoding access token:', e);
              }
            }
          },
          error: (err) => {
            console.error('Error getting access token:', err);
          }
        });
      } else {
        // User logged out, reset to public permissions
        console.log('User logged out, clearing permissions');
        this.permissions.clearPermissions();
      }
    });
  }

  // ============ TAB MANAGEMENT ============

  switchTab(tab: 'movies' | 'actors' | 'casting' | 'users') {
    this.activeTab = tab;
    this.clearMessages();
    if (tab === 'casting') {
      this.loadMoviesWithActors();
    } else if (tab === 'users') {
      this.loadUsers();
      this.loadAllRoles();
    }
  }

  // ============ MOVIE OPERATIONS ============

  loadMovies() {
    this.loading = true;
    this.apiService.getMovies().subscribe({
      next: (response) => {
        this.movies = response.movies || [];
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to load movies');
        this.loading = false;
      }
    });
  }

  createMovie() {
    if (!this.movieForm.title || !this.movieForm.release_date) {
      this.showError('Please fill in all movie fields');
      return;
    }

    this.loading = true;
    this.apiService.createMovie(this.movieForm).subscribe({
      next: (response) => {
        this.showSuccess('Movie created successfully!');
        this.loadMovies();
        this.resetMovieForm();
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to create movie');
        this.loading = false;
      }
    });
  }

  editMovie(movie: Movie) {
    this.isEditingMovie = true;
    this.movieForm = { ...movie };
    this.selectedMovie = movie;
  }

  updateMovie() {
    if (!this.selectedMovie?.id) return;

    this.loading = true;
    this.apiService.updateMovie(this.selectedMovie.id, this.movieForm).subscribe({
      next: (response) => {
        this.showSuccess('Movie updated successfully!');
        this.loadMovies();
        this.resetMovieForm();
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to update movie');
        this.loading = false;
      }
    });
  }

  deleteMovie(id: number) {
    if (!confirm('Are you sure you want to delete this movie?')) return;

    this.loading = true;
    this.apiService.deleteMovie(id).subscribe({
      next: (response) => {
        this.showSuccess('Movie deleted successfully!');
        this.loadMovies();
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to delete movie');
        this.loading = false;
      }
    });
  }

  resetMovieForm() {
    this.movieForm = { title: '', release_date: '' };
    this.selectedMovie = null;
    this.isEditingMovie = false;
  }

  // ============ ACTOR OPERATIONS ============

  loadActors() {
    this.loading = true;
    this.apiService.getActors().subscribe({
      next: (response) => {
        this.actors = response.actors || [];
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to load actors');
        this.loading = false;
      }
    });
  }

  createActor() {
    if (!this.actorForm.name || !this.actorForm.birth_date || !this.actorForm.gender) {
      this.showError('Please fill in all actor fields');
      return;
    }

    this.loading = true;
    this.apiService.createActor(this.actorForm).subscribe({
      next: (response) => {
        this.showSuccess('Actor created successfully!');
        this.loadActors();
        this.resetActorForm();
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to create actor');
        this.loading = false;
      }
    });
  }

  editActor(actor: Actor) {
    this.isEditingActor = true;
    this.actorForm = { ...actor };
    this.selectedActor = actor;
  }

  updateActor() {
    if (!this.selectedActor?.id) return;

    this.loading = true;
    this.apiService.updateActor(this.selectedActor.id, this.actorForm).subscribe({
      next: (response) => {
        this.showSuccess('Actor updated successfully!');
        this.loadActors();
        this.resetActorForm();
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to update actor');
        this.loading = false;
      }
    });
  }

  deleteActor(id: number) {
    if (!confirm('Are you sure you want to delete this actor?')) return;

    this.loading = true;
    this.apiService.deleteActor(id).subscribe({
      next: (response) => {
        this.showSuccess('Actor deleted successfully!');
        this.loadActors();
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to delete actor');
        this.loading = false;
      }
    });
  }

  resetActorForm() {
    this.actorForm = { name: '', birth_date: '', gender: '' };
    this.selectedActor = null;
    this.isEditingActor = false;
  }

  // ============ CASTING OPERATIONS ============

  loadMoviesWithActors() {
    this.loading = true;
    this.apiService.getMovies().subscribe({
      next: (response) => {
        this.movies = response.movies || [];
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to load movies');
        this.loading = false;
      }
    });
  }

  selectMovieForCasting(movie: Movie) {
    this.selectedMovieForCasting = movie;
    this.selectedActorForCasting = null;
    this.loadMovieActors(movie.id!);
    this.loadAvailableActors(movie.id!);
  }

  selectActorForCasting(actor: Actor) {
    this.selectedActorForCasting = actor;
    this.selectedMovieForCasting = null;
    this.loadActorMovies(actor.id!);
  }

  loadMovieActors(movieId: number) {
    this.loading = true;
    this.apiService.getMovieActors(movieId).subscribe({
      next: (response) => {
        this.movieActors = response.actors || [];
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to load movie actors');
        this.loading = false;
      }
    });
  }

  loadActorMovies(actorId: number) {
    this.loading = true;
    this.apiService.getActorMovies(actorId).subscribe({
      next: (response) => {
        this.actorMovies = response.movies || [];
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to load actor movies');
        this.loading = false;
      }
    });
  }

  loadAvailableActors(movieId: number) {
    this.apiService.getActors().subscribe({
      next: (response) => {
        const allActors = response.actors || [];
        // Filter out actors already in the movie
        this.availableActors = allActors.filter(actor =>
          !this.movieActors.some(ma => ma.id === actor.id)
        );
      },
      error: (error) => {
        this.showError('Failed to load actors');
      }
    });
  }

  assignActor(actorId: number) {
    if (!this.selectedMovieForCasting?.id) return;

    this.loading = true;
    this.apiService.assignActorToMovie(this.selectedMovieForCasting.id, actorId).subscribe({
      next: (response) => {
        this.showSuccess(response.message || 'Actor assigned successfully!');
        this.loadMovieActors(this.selectedMovieForCasting!.id!);
        this.loadAvailableActors(this.selectedMovieForCasting!.id!);
        this.loading = false;
      },
      error: (error) => {
        this.showError(error.error?.message || 'Failed to assign actor');
        this.loading = false;
      }
    });
  }

  removeActor(actorId: number) {
    if (!this.selectedMovieForCasting?.id) return;
    if (!confirm('Are you sure you want to remove this actor from the movie?')) return;

    this.loading = true;
    this.apiService.removeActorFromMovie(this.selectedMovieForCasting.id, actorId).subscribe({
      next: (response) => {
        this.showSuccess(response.message || 'Actor removed successfully!');
        this.loadMovieActors(this.selectedMovieForCasting!.id!);
        this.loadAvailableActors(this.selectedMovieForCasting!.id!);
        this.loading = false;
      },
      error: (error) => {
        this.showError(error.error?.message || 'Failed to remove actor');
        this.loading = false;
      }
    });
  }

  // ============ USER MANAGEMENT OPERATIONS ============

  loadUsers() {
    this.loading = true;
    this.apiService.getUsers(this.currentPage, this.perPage, this.searchQuery).subscribe({
      next: (response) => {
        this.users = response.users || [];
        this.totalUsers = response.total || 0;
        this.loading = false;
      },
      error: (error) => {
        this.showError('Failed to load users');
        this.loading = false;
      }
    });
  }

  loadAllRoles() {
    this.apiService.getAllRoles().subscribe({
      next: (response) => {
        this.availableRoles = response.roles || [];
      },
      error: (error) => {
        this.showError('Failed to load roles');
      }
    });
  }

  searchUsers() {
    this.currentPage = 0;
    this.loadUsers();
  }

  nextPage() {
    if ((this.currentPage + 1) * this.perPage < this.totalUsers) {
      this.currentPage++;
      this.loadUsers();
    }
  }

  previousPage() {
    if (this.currentPage > 0) {
      this.currentPage--;
      this.loadUsers();
    }
  }

  createUser() {
    if (!this.userForm.email || !this.userForm.password) {
      this.showError('Email and password are required');
      return;
    }

    this.loading = true;
    this.apiService.createUser(this.userForm).subscribe({
      next: (response) => {
        this.showSuccess('User created successfully!');
        this.loadUsers();
        this.resetUserForm();
        this.loading = false;
      },
      error: (error) => {
        this.showError(error.error?.message || 'Failed to create user');
        this.loading = false;
      }
    });
  }

  selectUser(user: User) {
    this.selectedUser = user;
    this.isEditingUser = false;
    this.loadUserRoles(user.user_id!);
  }

  editUser(user: User) {
    this.selectedUser = user;
    this.isEditingUser = true;
    this.userForm = {
      email: user.email || '',
      password: '',
      name: user.name || '',
      role: user.roles?.[0]?.name || 'Casting Assistant'
    };
  }

  updateUser() {
    if (!this.selectedUser?.user_id) return;

    const updates: any = {};
    if (this.userForm.name) updates.name = this.userForm.name;
    if (this.userForm.email) updates.email = this.userForm.email;

    this.loading = true;
    this.apiService.updateUser(this.selectedUser.user_id, updates).subscribe({
      next: (response) => {
        this.showSuccess('User updated successfully!');
        this.loadUsers();
        this.resetUserForm();
        this.loading = false;
      },
      error: (error) => {
        this.showError(error.error?.message || 'Failed to update user');
        this.loading = false;
      }
    });
  }

  deleteUser(userId: string) {
    if (!confirm('Are you sure you want to delete this user?')) return;

    this.loading = true;
    this.apiService.deleteUser(userId).subscribe({
      next: (response) => {
        this.showSuccess(response.message || 'User deleted successfully!');
        this.loadUsers();
        this.selectedUser = null;
        this.loading = false;
      },
      error: (error) => {
        this.showError(error.error?.message || 'Failed to delete user');
        this.loading = false;
      }
    });
  }

  loadUserRoles(userId: string) {
    this.apiService.getUserRoles(userId).subscribe({
      next: (response) => {
        this.selectedUserRoles = response.roles || [];
      },
      error: (error) => {
        this.showError('Failed to load user roles');
      }
    });
  }

  assignRole(roleId: string) {
    if (!this.selectedUser?.user_id) return;

    this.loading = true;
    this.apiService.assignUserRoles(this.selectedUser.user_id, [roleId]).subscribe({
      next: (response) => {
        this.showSuccess(response.message || 'Role assigned successfully!');
        this.loadUserRoles(this.selectedUser!.user_id!);
        this.loadUsers();
        this.loading = false;
      },
      error: (error) => {
        this.showError(error.error?.message || 'Failed to assign role');
        this.loading = false;
      }
    });
  }

  resetUserForm() {
    this.userForm = {
      email: '',
      password: '',
      name: '',
      role: 'Casting Assistant'
    };
    this.selectedUser = null;
    this.isEditingUser = false;
  }

  // ============ AUTHENTICATION ============

  login() {
    // Redirect to Auth0 login page
    this.auth.loginWithRedirect({
      appState: { target: '/movies' }
    });
  }

  logout() {
    // Clear permissions and logout from Auth0
    this.permissions.clearPermissions();
    this.auth.logout({
      logoutParams: {
        returnTo: window.location.origin
      }
    });

    // Reset to movies tab
    this.activeTab = 'movies';
  }

  // ============ UI HELPERS ============

  showError(message: string) {
    this.error = message;
    this.success = null;
    setTimeout(() => this.error = null, 5000);
  }

  showSuccess(message: string) {
    this.success = message;
    this.error = null;
    setTimeout(() => this.success = null, 5000);
  }

  clearMessages() {
    this.error = null;
    this.success = null;
  }
}
