import os
from services.cnd import gerar_cnd_federal
from services.tce_liberatoria import gerar_liberatoria_tce


PASTA_CERTIDOES = os.path.join(os.getcwd(), "certidoes")
os.makedirs(PASTA_CERTIDOES, exist_ok=True)

# ─────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────
# gerar_cnd_federal("75845503000167")

gerar_liberatoria_tce("75845503000167")