from enum import Enum


class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# What each role is allowed to do. Higher roles include all permissions of
# lower roles below them, but we spell them out explicitly here rather than
# relying on inheritance tricks — explicit is easier to audit and reason about.
ROLE_PERMISSIONS = {
    Role.OWNER: {"view", "chat", "upload", "delete_document", "manage_members", "delete_workspace"},
    Role.ADMIN: {"view", "chat", "upload", "delete_document", "manage_members"},
    Role.MEMBER: {"view", "chat", "upload"},
    Role.VIEWER: {"view", "chat"},
}


def role_has_permission(role: str, permission: str) -> bool:
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return permission in role_perms