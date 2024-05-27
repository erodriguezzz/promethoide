FROM httpd:2.4

# Copy configuration files
COPY proxy.conf /usr/local/apache2/conf/extra/proxy.conf

# Enable modules
RUN echo "LoadModule proxy_module modules/mod_proxy.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule proxy_http_module modules/mod_proxy_http.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule rewrite_module modules/mod_rewrite.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule cgi_module modules/mod_cgi.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "Include conf/extra/proxy.conf" >> /usr/local/apache2/conf/httpd.conf

# Copy files
COPY ./html/ /usr/local/apache2/htdocs/

# Copy delay script
COPY delay.sh /usr/local/apache2/cgi-bin/
RUN chmod +x /usr/local/apache2/cgi-bin/delay.sh

