import subprocess
import time
import re
from notify import send_message
from logger_config import setup_logger


HOSTS = [
    "www.instagram.com",
    "www.twitter.com",
]
RTT = 16
LOSS = 1.0
VARIATION = 1.5
WAIT_TIME: int = 10


def mtr_result(host) -> str:
    try:
        result = subprocess.run(
            ["mtr", "-r", "-c", "10", host], capture_output=True, text=True
        )
        return result.stdout
    except subprocess.SubprocessError as e:
        print(f"Error al ejecutar MTR para {host}: {e}")
        return ""


def hop_list(result) -> list:
    pattern = re.compile(
        r"\s*(\d{1,2})\.\|--\s+([^\s]+)\s+(\d+(\.\d+)?)%?\s+(\d+)\s+"
        r"([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)"
    )

    return [
        {
            "hop": int(match.group(1)),
            "host": match.group(2),
            "loss": float(match.group(3)),
            "rtt": float(match.group(7)),
            "jitter": (float(match.group(10))/float(match.group(7))) if float(match.group(7)) > 0 else 0,
        }
        for line in result.split("\n")
        if (match := pattern.match(line))
    ]


def path_analysis(host, current, previous) -> None:
    logger = setup_logger()
    previous_path = hop_list(previous)
    current_path = hop_list(current)

    try:
        is_path_changed = len(previous_path) != len(current_path)
        is_loss_increased = current_path[-1].get("loss") > LOSS
        is_rtt_increased = current_path[-1].get("rtt") > RTT
        is_connection_lost = current_path[-1]["loss"] == 100

        if is_connection_lost:
            send_message(f"Se perdió la conexión con {host}", current_path)
        elif is_path_changed or is_loss_increased or is_rtt_increased:
            check_for_changes(host, current_path, previous_path)
    except Exception as e:
        logger.error(e)


def check_for_changes(host, current_path, previous_path):
    path = current_path
    for prev_hop, curr_hop in zip(previous_path, current_path):
        if prev_hop["host"] != curr_hop["host"]:
            print_change(path, None, "path", host, curr_hop, prev_hop, "host")
            return
        elif (prev_hop["loss"] * VARIATION) < curr_hop["loss"] and current_path[-1].get(
            "loss"
        ) > LOSS:
            print_change(
                path,
                current_path[-1].get("loss"),
                "pérdida de paquetes",
                host,
                curr_hop,
                prev_hop,
                "loss",
            )
            return
        elif (prev_hop["rtt"] * VARIATION) < curr_hop["rtt"] and current_path[-1].get(
            "rtt"
        ) > RTT:
            print_change(
                path,
                current_path[-1].get("rtt"),
                "tiempo de respuesta",
                host,
                curr_hop,
                prev_hop,
                "rtt",
            )
            return


def print_change(path, stats, change_type, host, curr_hop, prev_hop, key):
    logger = setup_logger()
    current_val = curr_hop[key]
    previous_val = prev_hop[key]
    hop_num = curr_hop["hop"]

    if key in ["rtt", "loss"]:
        metric = "ms" if key == "rtt" else "%"
        message = (
            f"Se presentó un cambio en el {change_type} hacia {host} ahora es de {stats}{metric} "
            f"se identifica el fallo en el hop #{hop_num} \nSalto IP {curr_hop['host']}: "
            f"Medición anterior {previous_val}{metric} --> Medición actual {current_val}{metric}"
        )
    else:
        message = (
            f"Se presentó un recálculo en el {change_type} hacia {host} en el hop #{hop_num} "
            f"\nSalto IP {curr_hop['host']}: IP anterior {previous_val} --> IP actual {current_val}"
        )

    response = send_message(message, path)
    logger.info(response)


if __name__ == "__main__":
    previous_results = {host: None for host in HOSTS}

    while True:
        for host in HOSTS:
            current_result = mtr_result(host)
            previous_result = previous_results.get(host)

            if current_result and current_result != previous_result:
                if previous_result is not None:
                    path_analysis(host, current_result, previous_result)
                previous_results[host] = current_result
            elif previous_result is None:
                previous_results[host] = current_result
            else:
                print(
                    f"No hay diferencia para el host {host} entre el último y el actual resultado"
                )

        time.sleep(WAIT_TIME)
