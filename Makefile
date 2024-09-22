VENV_PATH = $(shell pwd)/.venv/bin/activate
# VERIZON = $(shell pwd)/web/verizon/main.py
# LAZADA = $(shell pwd)/web/lazada/main.py
# SUMMARY = $(shell pwd)/summary/main.py

AECO = $(shell pwd)/web/aeco/main.py
ALZA = $(shell pwd)/web/alza/main.py
ELCORTEINGLES = $(shell pwd)/web/elcorteingles/main.py
YOHO = $(shell pwd)/web/yoho/main.py

LOG_DIR = $(shell pwd)/logs

cron:
	@echo "Applying cron jobs..."
	@{ crontab -l; echo "0 5 * * * /bin/bash -c 'source $(VENV_PATH) && python $(AECO)' >> $(LOG_DIR)/aeco.log 2>&1"; } | crontab -
	@{ crontab -l; echo "5 5 * * * /bin/bash -c 'source $(VENV_PATH) && python $(ALZA)' >> $(LOG_DIR)/alza.log 2>&1"; } | crontab -
	@{ crontab -l; echo "10 5 * * * /bin/bash -c 'source $(VENV_PATH) && python $(ELCORTEINGLES)' >> $(LOG_DIR)/elcorteingles.log 2>&1"; } | crontab -
	@{ crontab -l; echo " 15 * * * /bin/bash -c 'source $(VENV_PATH) && python $(YOHO)' >> $(LOG_DIR)/yoho.log 2>&1"; } | crontab -
	@echo "Cron jobs applied successfully."

install:
	@echo "Installing dependencies..."
	@python3 -m venv .venv
	@source $(VENV_PATH) && pip install -r requirements.txt
	@echo "Dependencies installed successfully."
	@playwright install

clean-cron:
	@echo "Removing cron jobs..."
	@crontab -r
	@echo "Cron jobs removed successfully."