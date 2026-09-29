FROM python:3.14-slim
WORKDIR /app
COPY main.py .
RUN useradd -m appuser
ENV PYTHONDONTWRITEBYTECODE=1
USER appuser
EXPOSE 8000
CMD ["python3", "main.py"]
