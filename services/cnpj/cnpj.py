import os
import shutil
from dotenv import load_dotenv

load_dotenv()


def cnpj_75845503000167():

    # pasta destino vinda do .env
    pasta_destino = os.getenv(
        "PASTA_DOWNLOAD",
        os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "Certidoes"
        )
    )

    os.makedirs(pasta_destino, exist_ok=True)

    # PDF origem
    arquivo_origem = os.path.join(
        os.path.dirname(__file__),
        "cnpj.pdf"
    )

    # nome final
    arquivo_destino = os.path.join(
        pasta_destino,
        "cnpj.pdf"
    )

    # remove arquivo antigo
    if os.path.exists(arquivo_destino):
        os.remove(arquivo_destino)

    # copia PDF
    shutil.copy2(
        arquivo_origem,
        arquivo_destino
    )

    print("✅ PDF copiado com sucesso.")
    print(f"📄 Arquivo: {arquivo_destino}")

    return arquivo_destino