export interface Role {
  id: string;
  name: string;
  description?: string;
}

export interface User {
  user_id?: string;
  email?: string;
  name?: string;
  picture?: string;
  created_at?: string;
  updated_at?: string;
  roles?: Role[];
}

export interface UserResponse {
  success: boolean;
  user?: User;
  users?: User[];
  total?: number;
  page?: number;
  per_page?: number;
  your_role_level?: number;
  message?: string;
  deleted?: string;
  role_assigned?: string;
}

export interface RoleResponse {
  success: boolean;
  roles?: Role[];
  total?: number;
  your_role_level?: number;
  message?: string;
}
