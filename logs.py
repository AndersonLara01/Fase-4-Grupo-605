import logging

def configurar_logs():

    logging.basicConfig(
        filename="logs_sistema.log",
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8"
    )

    return logging.getLogger("SOFTWARE_FJ")


# Crear el logger
logger = configurar_logs()