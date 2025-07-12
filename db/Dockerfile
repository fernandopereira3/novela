# Use a specific version for reproducibility
FROM mongo:8.0
# Set the working directory
WORKDIR /data/db
# Copy the CSV and the import script to the initialization directory
COPY db.csv /docker-entrypoint-initdb.d/
COPY import.sh /docker-entrypoint-initdb.d/
# Make the import script executable
RUN chmod +x /docker-entrypoint-initdb.d/import.sh
RUN ./docker-entrypoint-initdb.d/import.sh
# Expose the default MongoDB port
EXPOSE 27017

