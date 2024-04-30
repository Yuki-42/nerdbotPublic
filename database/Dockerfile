FROM postgres:14-alpine

# Set environment variables
ENV POSTGRES_DB=bot
ENV POSTGRES_PASSWORD=Developer.1
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Copy the database initialization script into the container.
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# Expose the port that the database listens on.
EXPOSE 5432

# Switch to the postgres user.
USER postgres
