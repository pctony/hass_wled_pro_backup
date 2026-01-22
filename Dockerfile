FROM alpine:3.19

# Set Python to run unbuffered so logs appear immediately
ENV PYTHONUNBUFFERED=1

# Install Python and Requests
RUN apk add --no-cache python3 py3-requests

# Copy the backup engine
COPY backup.py /backup.py

# Run Python directly as the primary process
ENTRYPOINT ["python3", "/backup.py"]
