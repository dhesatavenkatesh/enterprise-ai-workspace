CREATE EXTENSION IF NOT EXISTS "pgcrypto";


DO $$
BEGIN
    CREATE TYPE message_role AS ENUM (
        'system',
        'user',
        'assistant'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;


DO $$
BEGIN
    CREATE TYPE prompt_status AS ENUM (
        'active',
        'inactive',
        'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;


CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id INTEGER NOT NULL,

    title VARCHAR(255)
        NOT NULL
        DEFAULT 'New Conversation',

    is_archived BOOLEAN
        NOT NULL
        DEFAULT FALSE,

    is_pinned BOOLEAN
        NOT NULL
        DEFAULT FALSE,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_conversations_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT ck_conversations_title_not_empty
        CHECK (char_length(trim(title)) > 0)
);


CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    conversation_id UUID NOT NULL,

    role message_role NOT NULL,

    content TEXT NOT NULL,

    token_count INTEGER
        NOT NULL
        DEFAULT 0,

    prompt_tokens INTEGER
        NOT NULL
        DEFAULT 0,

    completion_tokens INTEGER
        NOT NULL
        DEFAULT 0,

    provider VARCHAR(50),

    model_name VARCHAR(100),

    rating INTEGER,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_messages_conversation
        FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE,

    CONSTRAINT ck_messages_content_not_empty
        CHECK (char_length(trim(content)) > 0),

    CONSTRAINT ck_messages_token_count_non_negative
        CHECK (token_count >= 0),

    CONSTRAINT ck_messages_prompt_tokens_non_negative
        CHECK (prompt_tokens >= 0),

    CONSTRAINT ck_messages_completion_tokens_non_negative
        CHECK (completion_tokens >= 0),

    CONSTRAINT ck_messages_rating_range
        CHECK (
            rating IS NULL
            OR rating BETWEEN 1 AND 5
        )
);


CREATE TABLE IF NOT EXISTS prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id INTEGER,

    name VARCHAR(150) NOT NULL,

    system_prompt TEXT NOT NULL,

    description TEXT,

    category VARCHAR(100)
        NOT NULL
        DEFAULT 'General',

    status prompt_status
        NOT NULL
        DEFAULT 'active',

    is_favorite BOOLEAN
        NOT NULL
        DEFAULT FALSE,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_prompt_templates_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT ck_prompt_templates_name_not_empty
        CHECK (char_length(trim(name)) > 0),

    CONSTRAINT ck_prompt_templates_prompt_not_empty
        CHECK (char_length(trim(system_prompt)) > 0)
);


CREATE INDEX IF NOT EXISTS ix_conversations_user_id
    ON conversations(user_id);


CREATE INDEX IF NOT EXISTS ix_conversations_user_updated_at
    ON conversations(user_id, updated_at DESC);


CREATE INDEX IF NOT EXISTS ix_conversations_user_archived
    ON conversations(user_id, is_archived);


CREATE INDEX IF NOT EXISTS ix_conversations_user_pinned
    ON conversations(user_id, is_pinned);


CREATE INDEX IF NOT EXISTS ix_messages_conversation_id
    ON messages(conversation_id);


CREATE INDEX IF NOT EXISTS ix_messages_conversation_created_at
    ON messages(conversation_id, created_at);


CREATE INDEX IF NOT EXISTS ix_messages_role
    ON messages(role);


CREATE INDEX IF NOT EXISTS ix_messages_model_name
    ON messages(model_name);


CREATE INDEX IF NOT EXISTS ix_prompt_templates_user_id
    ON prompt_templates(user_id);


CREATE INDEX IF NOT EXISTS ix_prompt_templates_user_category
    ON prompt_templates(user_id, category);


CREATE INDEX IF NOT EXISTS ix_prompt_templates_status
    ON prompt_templates(status);


CREATE INDEX IF NOT EXISTS ix_prompt_templates_favorite
    ON prompt_templates(user_id, is_favorite);


CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS conversations_set_updated_at
ON conversations;


CREATE TRIGGER conversations_set_updated_at
BEFORE UPDATE ON conversations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


DROP TRIGGER IF EXISTS prompt_templates_set_updated_at
ON prompt_templates;


CREATE TRIGGER prompt_templates_set_updated_at
BEFORE UPDATE ON prompt_templates
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();