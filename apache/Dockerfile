# Usa la imagen base de Apache
FROM httpd:2.4

# Copia la configuración del proxy inverso
COPY proxy.conf /usr/local/apache2/conf/extra/proxy.conf

# Carga módulos de proxy
RUN echo "LoadModule proxy_module modules/mod_proxy.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule proxy_http_module modules/mod_proxy_http.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "Include conf/extra/proxy.conf" >> /usr/local/apache2/conf/httpd.conf

# Copia archivos HTML/CSS/JS al directorio adecuado
COPY . /usr/local/apache2/htdocs/