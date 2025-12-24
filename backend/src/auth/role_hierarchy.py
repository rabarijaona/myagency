from flask import abort, jsonify

ROLE_HIERARCHY = {
    'Casting Assistant': 1,
    'Casting Director': 2,
    'Executive Producer': 3
}

CASTING_ASSISTANT_ROLE = 'Casting Assistant'
CASTING_DIRECTOR_ROLE = 'Casting Director'
EXECUTIVE_PRODUCER_ROLE = 'Executive Producer'


def get_user_role_level(permissions):
    if not permissions:
        return 0

    if 'delete:movies' in permissions and 'post:movies' in permissions:
        return ROLE_HIERARCHY['Executive Producer']

    if 'delete:actors' in permissions or 'post:actors' in permissions:
        return ROLE_HIERARCHY['Casting Director']

    if 'get:movies' in permissions or 'get:actors' in permissions:
        return ROLE_HIERARCHY['Casting Assistant']

    return 0


def get_role_name_from_level(level):
    for role, lvl in ROLE_HIERARCHY.items():
        if lvl == level:
            return role
    return None


def can_manage_user(manager_permissions, target_user_roles):
    manager_level = get_user_role_level(manager_permissions)

    if manager_level == 0:
        return False, "No management permissions"

    target_level = 0
    for role in target_user_roles:
        role_name = role.get('name', '')
        if role_name in ROLE_HIERARCHY:
            level = ROLE_HIERARCHY[role_name]
            if level > target_level:
                target_level = level

    if manager_level == ROLE_HIERARCHY['Executive Producer']:
        if target_level == ROLE_HIERARCHY['Executive Producer']:
            return False, "Executive Producers cannot manage other Executive Producers"
        return True, None

    if manager_level == ROLE_HIERARCHY['Casting Director']:
        if target_level > ROLE_HIERARCHY['Casting Assistant']:
            return False, "Casting Directors can only manage Casting Assistant users"
        return True, None

    return False, "Insufficient permissions to manage users"


def can_assign_role(manager_permissions, role_name):
    manager_level = get_user_role_level(manager_permissions)

    if role_name not in ROLE_HIERARCHY:
        return False, f"Invalid role: {role_name}"

    target_role_level = ROLE_HIERARCHY[role_name]

    if manager_level == ROLE_HIERARCHY['Executive Producer']:
        if target_role_level == ROLE_HIERARCHY['Executive Producer']:
            return False, "Cannot assign Executive Producer role via API"
        return True, None

    if manager_level == ROLE_HIERARCHY['Casting Director']:
        if target_role_level == ROLE_HIERARCHY['Casting Assistant']:
            return True, None
        return False, "Casting Directors can only assign Casting Assistant role"

    return False, "Insufficient permissions to assign roles"


def filter_users_by_access_level(users, manager_permissions):
    manager_level = get_user_role_level(manager_permissions)

    if manager_level == ROLE_HIERARCHY['Executive Producer']:
        return users

    if manager_level == ROLE_HIERARCHY['Casting Director']:
        filtered_users = []
        for user in users:
            user_perms = user.get('permissions', [])
            user_level = get_user_role_level(user_perms)
            if user_level <= ROLE_HIERARCHY['Casting Assistant']:
                filtered_users.append(user)
        return filtered_users

    return []


def enforce_user_management_access(manager_permissions, target_user_roles):
    can_manage, error = can_manage_user(manager_permissions, target_user_roles)
    if not can_manage:
        abort(403, description=error)


def enforce_role_assignment_access(manager_permissions, role_name):
    can_assign, error = can_assign_role(manager_permissions, role_name)
    if not can_assign:
        abort(403, description=error)


def get_assignable_roles(manager_permissions, all_roles):
    manager_level = get_user_role_level(manager_permissions)

    assignable = []
    for role in all_roles:
        role_name = role.get('name', '')
        if role_name in ROLE_HIERARCHY:
            role_level = ROLE_HIERARCHY[role_name]

            if manager_level == ROLE_HIERARCHY['Executive Producer']:
                if role_level < ROLE_HIERARCHY['Executive Producer']:
                    assignable.append(role)

            elif manager_level == ROLE_HIERARCHY['Casting Director']:
                if role_level == ROLE_HIERARCHY['Casting Assistant']:
                    assignable.append(role)

    return assignable
