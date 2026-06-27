FROM odoo:17

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext-base \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install qifparse --no-cache-dir

COPY addons/ /mnt/extra-addons/
COPY config/odoo.conf.template /etc/odoo/odoo.conf.template
COPY entrypoint.sh /entrypoint-custom.sh
RUN chmod +x /entrypoint-custom.sh

USER odoo
ENTRYPOINT ["/entrypoint-custom.sh"]
