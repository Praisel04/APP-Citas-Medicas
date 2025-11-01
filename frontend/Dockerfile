FROM nginx:alpine

# Eliminamos contenido por defecto
RUN rm -rf /usr/share/nginx/html/*

# Copiamos los archivos HTML y estáticos
COPY ./templates /usr/share/nginx/html
COPY ./static /usr/share/nginx/html/static

# Copiamos la configuración personalizada
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
