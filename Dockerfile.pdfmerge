FROM python:3.11-slim

WORKDIR /app

RUN pip install flask PyPDF2

COPY pdf_merge_service.py .

EXPOSE 3000

CMD ["python", "pdf_merge_service.py"]
