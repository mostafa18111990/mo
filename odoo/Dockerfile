FROM odoo:17

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext-base \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install qifparse --no-cache-dir

# Download base_accounting_kit community module
RUN git clone --depth=1 --filter=blob:none --sparse \
    https://github.com/CybroOdoo/CybroAddons.git /tmp/cybros && \
    cd /tmp/cybros && \
    git sparse-checkout set base_accounting_kit && \
    cp -r base_accounting_kit /mnt/extra-addons/ && \
    rm -rf /tmp/cybros

COPY addons/ /mnt/extra-addons/
COPY config/odoo.conf.template /etc/odoo/odoo.conf.template
COPY entrypoint.sh /entrypoint-custom.sh
RUN chmod +x /entrypoint-custom.sh

USER odoo
ENTRYPOINT ["/entrypoint-custom.sh"]
