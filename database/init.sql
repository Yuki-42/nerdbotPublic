CREATE ROLE bot WITH LOGIN PASSWORD 'bot';

/* Move to the database that was automatically created */
\c bot

/* Add UUID extension */
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

/* Create schemas */
CREATE SCHEMA reply;
CREATE SCHEMA filter;
CREATE SCHEMA reactions;
CREATE SCHEMA logs;

/* Create tables */
CREATE TABLE logs.commands (
    id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    command TEXT NOT NULL,
    args TEXT[] NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE,
    FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE
);

CREATE TABLE public.users (
    id BIGINT NOT NULL,  /* Discord ID */
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    username TEXT NOT NULL,
    banned BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id)
);

CREATE TABLE public.guilds (
    id BIGINT NOT NULL,  /* Discord ID */
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    name TEXT NOT NULL,
    prefix TEXT NOT NULL DEFAULT '!',
    slash_commands BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id)
);

CREATE TABLE public.guilds_users (
    id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    message_tracking BOOLEAN NOT NULL DEFAULT TRUE,
    messages_sent BIGINT NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE,
    FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE
);

CREATE TABLE public.guilds_channels (
    id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    channel_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    message_tracking BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id),
    FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE
);

/*
What I want to be able to do:
- Toggle replies matching specific regexes for all replies in a guild,
- Toggle replies matching specific regexes for all replies from a specific user in a specific guild
- Toggle replies matching specific regexes for all replies from a specific user in all guilds
*/
CREATE TABLE reply.filters (
    id UUID DEFAULT uuid_generate_v4(),
    applies_to BIGINT NOT NULL,  /* User who's replies are filtered */
    guild_id BIGINT,
    channel_id BIGINT,
    user_id BIGINT,
    regex TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id),
    FOREIGN KEY (applies_to) REFERENCES public.users(id) ON DELETE CASCADE,
    FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

/* What I want to be able to do
- Automatically delete messages that match a specific regex globally
- Automatically delete messages that match a specific regex in a specific guild
- Automatically delete messages that match a specific regex from a specific user in a specific guild
- Automatically delete messages that match a specific regex from a specific user in all guilds
*/

CREATE TABLE filter.filters (
    id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    guild_id BIGINT,
    channel_id BIGINT,
    user_id BIGINT,
    regex TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id),
    FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

CREATE TABLE reactions.reactions (
    id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    guild_id BIGINT,
    channel_id BIGINT,
    user_id BIGINT NOT NULL,
    emoji TEXT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);