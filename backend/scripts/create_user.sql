-- SQL script to create admin user
-- This will insert the user directly using SQL

-- First, let's create a hash for password "Maya100$"
-- Using Python's passlib as reference, but we'll need to compute this differently

-- Insert the admin user with a temporary simple hash
-- You can then login and change the password through the UI

INSERT INTO users (email, full_name, hashed_password, is_admin, is_active, created_at, updated_at)
VALUES (
    'nixonlauture@gmail.com',
    'Nixon Lauture',
    '$2b$12$KIXFqZQ8vGZG8z0ZZqGqCeYZqGqCeYZqGqCeYZqGqCeYZqGqCeYZqG',  -- Placeholder, needs proper hash
    true,
    true,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;
