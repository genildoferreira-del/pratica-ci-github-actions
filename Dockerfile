# Imagem oficial e enxuta do Python (versao suportada)
FROM python:3.12-slim
 
# Aplica as correcoes de seguranca do sistema operacional da imagem base
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app
 
# Copia so as dependencias primeiro (aproveita o cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
# Dentro do conteiner a API precisa escutar em todas as interfaces
ENV FLASK_HOST=0.0.0.0
# A Feature Flag nasce DESLIGADA; ligue com: docker run -e FEATURE_DESCONTO_PROMO=true
ENV FEATURE_DESCONTO_PROMO=false
 
EXPOSE 5000
 
CMD ["python", "app.py"]
 