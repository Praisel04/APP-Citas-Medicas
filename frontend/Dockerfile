# Etapa única: usar nginx como base para servir archivos estáticos
FROM nginx:alpine

# Eliminamos la configuración por defecto y copiamos nuestra web
RUN rm -rf /usr/share/nginx/html/*

# Copiamos la web construida dentro del contenedor
COPY ./templates /usr/share/nginx/html

COPY ./static /usr/share/nginx/html/static

# Opcional: si quieres configuración propia de Nginx
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
