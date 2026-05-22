import os
from services.cnd_federal import gerar_cnd_federal
from services.tce_liberatoria import gerar_liberatoria_tce
from services.fgts import gerar_crf_fgts
from services.cnd_estadual import gerar_certidao_fazenda_pr
from services.trasnferencias_voluntarias import gerar_certidao_transferencia_voluntaria

PASTA_CERTIDOES = os.path.join(os.getcwd(), "certidoes")
os.makedirs(PASTA_CERTIDOES, exist_ok=True)

CNPJ = "75845503000167"

# ─────────────────────────────────────────────
# EXECUÇÃO
# ─────────────────────────────────────────────


#gerar_cnd_federal(CNPJ)


if True == True:
    gerar_certidao_transferencia_voluntaria(CNPJ)
    gerar_liberatoria_tce(CNPJ)
    gerar_crf_fgts(CNPJ)
    gerar_certidao_fazenda_pr(CNPJ)

else:
    pass
