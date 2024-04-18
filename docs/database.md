# Database

The database for the project will be a PostgreSQL database hosted locally on the server. The database will store all 
persistent data for the project. This includes data such as user information and game information. The database will be
accessed using the `psycopg2` library in Python through the use of the `psycopg2.extras.RealDictCursor` cursor to return
results as dictionaries. This will be wrapped in a custom `Database` class that will handle all database interactions.

## Tables

All tables in the database will have an `id` column that acts the primary key for the table. This column will be a `SERIAL`
column that auto-increments. The `id` column will be the first column in all tables. There is one exception to this rule,
the `users` table will have an `id` column that is a BIGINT instead of a SERIAL. This is because the `id` column in the
`users` table will be the Discord user ID of the user. This will allow for easy access to user information based on the
user's Discord ID. The same goes for the `guilds` table. 
All tables will also have a `created_at` column that will store the date and time the row was created. This column will
have a default value of `CURRENT_TIMESTAMP` and will be set to the current date and time when a new row is inserted. This
column will be the 2nd column in all tables.

## Many-to-Many Relationships

Some tables will have many-to-many relationships. These relationships will be handled using a separate table that will
store the IDs of the two tables that are related. These tables will comply with the naming convention of `table1_table2`
where `table1` and `table2` are the names of the tables that are related. These tables will also comply with the above [rules](#tables).

The foreign keys in these tables must be set to `ON DELETE CASCADE` and `ON UPDATE CASCADE` to ensure that when a row is deleted from one of the
related tables, the row is also deleted from the relationship table.

The foreign keys must also follow the naming convention of `table1_id` and `table2_id` where `table1` and `table2` are the names of the tables that are related.

### users

The `users` table will store information about users of the bot. Note: Due to the recent changes to discord's users system, there is no longer a need to store the discriminator of the user. 

This table will have the following columns:
 
| Column Name | Data Type | Nullable | Default           | Description                              | Extra       | Example             |
|-------------|-----------|----------|-------------------|------------------------------------------|-------------|---------------------|
| id          | BIGINT    | No       |                   | The Discord user ID of the user          | PRIMARY KEY | 123456789012345678  |
| created_at  | TIMESTAMP | No       | CURRENT_TIMESTAMP | The date and time the row was created.   |             | 2021-01-01 12:00:00 |
| username    | TEXT      | No       |                   | The username of the user.                |             | Nerdbot             |
| banned      | BOOLEAN   | No       | FALSE             | Whether the user is banned from the bot. |             | FALSE               |

### block_replies 

The `block_replies` table will store information about users that have been banned from replying to other users with specific messages.

This table will have the following columns:

| Column Name  | Data Type | Default           | Description                            | Extra       | Example             |
|--------------|-----------|-------------------|----------------------------------------|-------------|---------------------|
| id           | SERIAL    |                   | The ID of the row.                     | PRIMARY KEY | 1                   |
| created_at   | TIMESTAMP | CURRENT_TIMESTAMP | The date and time the row was created. |             | 2021-01-01 12:00:00 |
| user_id      | BIGINT    |                   | The ID of the user.                    | FOREIGN KEY | 123                 |
| blocked_user | BIGINT    |                   | The ID of the user that is blocked.    | FOREIGN KEY | 123                 |
| message      | TEXT      |                   | The message that is blocked.           |             | Hello               |

### guilds

The `guilds` table will store information about guilds that the bot is in.

This table will have the following columns:

| Column Name   | Data Type | Default           | Description                            | Extra       | Example             |
|---------------|-----------|-------------------|----------------------------------------|-------------|---------------------|
| id            | BIGINT    |                   | The ID of the guild.                   | PRIMARY KEY | 1                   |
| created_at    | TIMESTAMP | CURRENT_TIMESTAMP | The date and time the row was created. |             | 2021-01-01 12:00:00 |
| name          | TEXT      |                   | The name of the guild.                 |             | Nerdbot Guild       |

### user_guilds

The `user_guilds` table will store the relationship between users and guilds. This table will store the IDs of the user
and the guild that are related.

This table will have the following columns:

| Column Name   | Data Type | Default           | Description                                           | Extra       | Example             |
|---------------|-----------|-------------------|-------------------------------------------------------|-------------|---------------------|
| id            | SERIAL    |                   | The ID of the row.                                    | PRIMARY KEY | 1                   |
| created_at    | TIMESTAMP | CURRENT_TIMESTAMP | The date and time the row was created.                |             | 2021-01-01 12:00:00 |
| user_id       | BIGINT    |                   | The ID of the user.                                   | FOREIGN KEY | 123                 |     
| guild_id      | BIGINT    |                   | The ID of the guild.                                  | FOREIGN KEY | 1                   |
| message_count | INT       | 0                 | The number of messages sent by the user in the guild. |             | 100                 |

### reactions

The `reactions` table will store information about automatic reactions that the bot will add to messages.

This table will have the following columns:

| Column Name | Data Type | Default           | Description                                        | Extra       | Example             |
|-------------|-----------|-------------------|----------------------------------------------------|-------------|---------------------|
| id          | SERIAL    |                   | The ID of the row.                                 | PRIMARY KEY | 1                   |
| created_at  | TIMESTAMP | CURRENT_TIMESTAMP | The date and time the row was created.             |             | 2021-01-01 12:00:00 |
| guild_id    | BIGINT    |                   | The ID of the guild. 0 to apply to all guilds.     | FOREIGN KEY | 1                   |
| channel_id  | BIGINT    |                   | The ID of the channel. 0 to apply to all channels. | FOREIGN KEY | 1                   |
| user_id     | BIGINT    |                   | The ID of the user.                                | FOREIGN KEY | 123                 |
| added_by    | BIGINT    |                   | The ID of the user that added the reaction.        | FOREIGN KEY | 123                 |
| emoji       | TEXT      |                   | The emoji.                                         |             | :smile:             |

### banned_text

The `banned_text` table will store banned text that will be automatically deleted by the bot.

This table will have the following columns:

| Column Name | Data Type | Default           | Description                                                        | Extra       | Example             |
|-------------|-----------|-------------------|--------------------------------------------------------------------|-------------|---------------------|
| id          | SERIAL    |                   | The ID of the row.                                                 | PRIMARY KEY | 1                   |
| created_at  | TIMESTAMP | CURRENT_TIMESTAMP | The date and time the row was created.                             |             | 2021-01-01 12:00:00 |
| guild_id    | BIGINT    |                   | The ID of the guild. 0 to apply to all guilds.                     | FOREIGN KEY | 1                   |
| channel_id  | BIGINT    |                   | The ID of the channel. 0 to apply to all channels.                 | FOREIGN KEY | 1                   |
| user_id     | BIGINT    |                   | The ID of the user to apply this rule to. 0 to apply to all users. | FOREIGN KEY | 123                 |
| added_by    | BIGINT    |                   | The ID of the user that added the banned text.                     | FOREIGN KEY | 123                 |
| text        | TEXT      |                   | The text that is banned.                                           |             | bad word            |
| reason      | TEXT      |                   | The reason the text is banned.                                     |             | Profanity           |