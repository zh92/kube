FROM python:3.14-slim
WORKDIR /app
COPY main.py .
RUN useradd -m appuser && chown -R appuser /app
ENV PYTHONDONTWRITEBYTECODE=1
USER appuser
EXPOSE 8000
CMD ["python3", "main.py"]
