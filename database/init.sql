CREATE ROLE bot WITH LOGIN;
ALTER ROLE bot WITH ENCRYPTED PASSWORD 'Developer.1';

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
    PRIMARY KEY (id)
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
    PRIMARY KEY (id)
);

CREATE TABLE public.guilds_channels (
    id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    channel_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    message_tracking BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id)
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
    PRIMARY KEY (id)
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
    PRIMARY KEY (id)
);

CREATE TABLE reactions.reactions (
    id UUID DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    guild_id BIGINT,
    channel_id BIGINT,
    user_id BIGINT NOT NULL,
    emoji TEXT NOT NULL,
    PRIMARY KEY (id)
);

/* Create indexes */
CREATE INDEX idx_commands_user_id ON logs.commands(user_id);
CREATE INDEX idx_commands_guild_id ON logs.commands(guild_id);

CREATE INDEX idx_users_id ON public.users(id);

CREATE INDEX idx_guilds_id ON public.guilds(id);

CREATE INDEX idx_guilds_users_user_id ON public.guilds_users(user_id);
CREATE INDEX idx_guilds_users_guild_id ON public.guilds_users(guild_id);

CREATE INDEX idx_guilds_channels_channel_id ON public.guilds_channels(channel_id);
CREATE INDEX idx_guilds_channels_guild_id ON public.guilds_channels(guild_id);

CREATE INDEX idx_reply_filters_applies_to ON reply.filters(applies_to);
CREATE INDEX idx_reply_filters_guild_id ON reply.filters(guild_id);
CREATE INDEX idx_reply_filters_user_id ON reply.filters(user_id);

CREATE INDEX idx_filter_filters_guild_id ON filter.filters(guild_id);
CREATE INDEX idx_filter_filters_user_id ON filter.filters(user_id);

CREATE INDEX idx_reactions_guild_id ON reactions.reactions(guild_id);
CREATE INDEX idx_reactions_user_id ON reactions.reactions(user_id);

/* Create Foreign Keys */
ALTER TABLE logs.commands ADD FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE logs.commands ADD FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE;

ALTER TABLE public.guilds_users ADD FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE public.guilds_users ADD FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE public.guilds_channels ADD FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE;

ALTER TABLE reply.filters ADD FOREIGN KEY (applies_to) REFERENCES public.users(id) ON DELETE CASCADE;
ALTER TABLE reply.filters ADD FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE;
ALTER TABLE reply.filters ADD FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE filter.filters ADD FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE;
ALTER TABLE filter.filters ADD FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE reactions.reactions ADD FOREIGN KEY (guild_id) REFERENCES public.guilds(id) ON DELETE CASCADE;
ALTER TABLE reactions.reactions ADD FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

/* Grant permissions */
GRANT ALL PRIVILEGES ON DATABASE bot TO bot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA reply TO bot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA filter TO bot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA reactions TO bot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA logs TO bot;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO bot;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA reply TO bot;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA filter TO bot;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA reactions TO bot;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA logs TO bot;

/* Add autofill data */
INSERT INTO public.users (id, username) VALUES (1, 'System');
INSERT INTO public.guilds (id, name) VALUES (1, 'System');
