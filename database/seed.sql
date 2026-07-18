INSERT INTO roles (
    name,
    description
)
VALUES
    (
        'Admin',
        'Full system access'
    ),
    (
        'HR',
        'Human resources module access'
    ),
    (
        'Employee',
        'Standard employee access'
    ),
    (
        'Manager',
        'Manager and team access'
    ),
    (
        'Support',
        'Support module access'
    )
ON CONFLICT (name) DO NOTHING;


INSERT INTO permissions (
    permission_name,
    module,
    description
)
VALUES
    (
        'admin.full_access',
        'admin',
        'Full administrative access'
    ),
    (
        'hr.access',
        'hr',
        'Access HR module'
    ),
    (
        'chat.access',
        'ai_chat',
        'Access AI chat'
    ),
    (
        'manager.access',
        'manager',
        'Access manager module'
    ),
    (
        'support.access',
        'support',
        'Access support module'
    )
ON CONFLICT (
    permission_name,
    module
) DO NOTHING;


INSERT INTO role_permissions (
    role_id,
    permission_id
)
SELECT
    roles.id,
    permissions.id
FROM roles
JOIN permissions
    ON permissions.permission_name IN (
        'admin.full_access',
        'hr.access',
        'chat.access',
        'manager.access',
        'support.access'
    )
WHERE roles.name = 'Admin'
ON CONFLICT (
    role_id,
    permission_id
) DO NOTHING;


INSERT INTO role_permissions (
    role_id,
    permission_id
)
SELECT
    roles.id,
    permissions.id
FROM roles
JOIN permissions
    ON permissions.permission_name IN (
        'hr.access',
        'chat.access'
    )
WHERE roles.name = 'HR'
ON CONFLICT (
    role_id,
    permission_id
) DO NOTHING;


INSERT INTO role_permissions (
    role_id,
    permission_id
)
SELECT
    roles.id,
    permissions.id
FROM roles
JOIN permissions
    ON permissions.permission_name = 'chat.access'
WHERE roles.name = 'Employee'
ON CONFLICT (
    role_id,
    permission_id
) DO NOTHING;


INSERT INTO role_permissions (
    role_id,
    permission_id
)
SELECT
    roles.id,
    permissions.id
FROM roles
JOIN permissions
    ON permissions.permission_name IN (
        'manager.access',
        'chat.access'
    )
WHERE roles.name = 'Manager'
ON CONFLICT (
    role_id,
    permission_id
) DO NOTHING;


INSERT INTO role_permissions (
    role_id,
    permission_id
)
SELECT
    roles.id,
    permissions.id
FROM roles
JOIN permissions
    ON permissions.permission_name IN (
        'support.access',
        'chat.access'
    )
WHERE roles.name = 'Support'
ON CONFLICT (
    role_id,
    permission_id
) DO NOTHING;