import { Injectable } from '@angular/core';

export type Permission =
  | 'get:movies' | 'post:movies' | 'patch:movies' | 'delete:movies'
  | 'get:actors' | 'post:actors' | 'patch:actors' | 'delete:actors'
  | 'post:casting' | 'delete:casting'
  | 'get:users' | 'post:users' | 'patch:users' | 'delete:users';

export type Role = 'Public' | 'Casting Assistant' | 'Casting Director' | 'Executive Producer';

@Injectable({
  providedIn: 'root'
})
export class PermissionService {
  // Current user permissions (in development, we simulate Executive Producer)
  private currentPermissions: Permission[] = [];
  private currentRole: Role = 'Public';

  // Define role permissions
  private rolePermissions: Record<Role, Permission[]> = {
    'Public': ['get:movies', 'get:actors'],
    'Casting Assistant': ['get:movies', 'get:actors'],
    'Casting Director': [
      'get:movies', 'patch:movies',
      'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
      'post:casting', 'delete:casting',
      'get:users', 'post:users', 'patch:users', 'delete:users'
    ],
    'Executive Producer': [
      'get:movies', 'post:movies', 'patch:movies', 'delete:movies',
      'get:actors', 'post:actors', 'patch:actors', 'delete:actors',
      'post:casting', 'delete:casting',
      'get:users', 'post:users', 'patch:users', 'delete:users'
    ]
  };

  constructor() {
    this.setRole('Casting Assistant');
  }

  /**
   * Set the current user's role (for development/testing)
   * In production, this would be derived from JWT token
   */
  setRole(role: Role): void {
    this.currentRole = role;
    this.currentPermissions = this.rolePermissions[role];
  }

  /**
   * Get the current user's role
   */
  getRole(): Role {
    return this.currentRole;
  }

  /**
   * Check if the current user has a specific permission
   */
  hasPermission(permission: Permission): boolean {
    return this.currentPermissions.includes(permission);
  }

  /**
   * Check if the current user has any of the specified permissions
   */
  hasAnyPermission(...permissions: Permission[]): boolean {
    return permissions.some(permission => this.hasPermission(permission));
  }

  /**
   * Check if user can create movies
   */
  canCreateMovies(): boolean {
    return this.hasPermission('post:movies');
  }

  /**
   * Check if user can edit movies
   */
  canEditMovies(): boolean {
    return this.hasPermission('patch:movies');
  }

  /**
   * Check if user can delete movies
   */
  canDeleteMovies(): boolean {
    return this.hasPermission('delete:movies');
  }

  /**
   * Check if user can view actors (public access)
   */
  canViewActors(): boolean {
    return true; // Public access
  }

  /**
   * Check if user can create actors
   */
  canCreateActors(): boolean {
    return this.hasPermission('post:actors');
  }

  /**
   * Check if user can edit actors
   */
  canEditActors(): boolean {
    return this.hasPermission('patch:actors');
  }

  /**
   * Check if user can delete actors
   */
  canDeleteActors(): boolean {
    return this.hasPermission('delete:actors');
  }

  /**
   * Check if user can manage casting (assign/remove actors from movies)
   */
  canManageCasting(): boolean {
    return this.hasAnyPermission('post:casting', 'delete:casting');
  }

  /**
   * Check if user can view users tab
   */
  canViewUsers(): boolean {
    return this.hasPermission('get:users');
  }

  /**
   * Check if user can create users
   */
  canCreateUsers(): boolean {
    return this.hasPermission('post:users');
  }

  /**
   * Check if user can edit users
   */
  canEditUsers(): boolean {
    return this.hasPermission('patch:users');
  }

  /**
   * Check if user can delete users
   */
  canDeleteUsers(): boolean {
    return this.hasPermission('delete:users');
  }

  setPermissionsFromToken(payload: any): void {
    let permissions: string[] = [];

    if (Array.isArray(payload.permissions)) {
      permissions = payload.permissions;
    } else {
      const namespaceKeys = Object.keys(payload).filter(key =>
        key.includes('permissions') || key.includes('/permissions')
      );

      if (namespaceKeys.length > 0) {
        const permKey = namespaceKeys[0];
        if (Array.isArray(payload[permKey])) {
          permissions = payload[permKey];
        }
      }
    }

    if (permissions.length > 0) {
      this.currentPermissions = permissions as Permission[];

      if (this.hasPermission('delete:movies') && this.hasPermission('post:movies')) {
        this.currentRole = 'Executive Producer';
      } else if (this.hasPermission('delete:actors') || this.hasPermission('post:actors')) {
        this.currentRole = 'Casting Director';
      } else if (this.hasPermission('get:movies') || this.hasPermission('get:actors')) {
        this.currentRole = 'Casting Assistant';
      } else {
        this.currentRole = 'Public';
      }

    } else {
      this.currentRole = 'Public';
      this.currentPermissions = this.rolePermissions['Public'];
    }
  }

  /**
   * Clear all permissions (logout)
   */
  clearPermissions(): void {
    this.currentRole = 'Public';
    this.currentPermissions = this.rolePermissions['Public'];
  }
}
