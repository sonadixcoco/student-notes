FROM python:3.11-slim
WORKDIR /app
COPY app.py .
ENV PORT=8202 DATA_DIR=/data PYTHONUNBUFFERED=1
RUN mkdir -p /data && useradd -m appuser && chown -R appuser /data
USER appuser
EXPOSE 8202
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8202/health').status==200 else 1)"
CMD ["python", "app.py"]