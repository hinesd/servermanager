ARG JAVA_VERSION=21
FROM eclipse-temurin:${JAVA_VERSION}-jdk AS java-builder

FROM python:3.12
WORKDIR /app
# Copy Java from the java-base stage
COPY --from=java-builder /opt/java/openjdk /opt/java/openjdk
# Set up Java environment variables
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

COPY src/server_controller/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/server_controller /app/server_controller
COPY src/settings /app/server_controller/settings
COPY server /app/server


CMD ["python", "server_controller/main.py"]