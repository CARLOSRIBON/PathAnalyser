import subprocess
import time
import re
from notify import send_message

HOSTS = [
    "www.instagram.com",
    "www.twitter.com",
]
RTT = 16
LOSS = 1
VARIATION = 1.5


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
            "sent": int(match.group(5)),
            "last": float(match.group(6)),
            "avg": float(match.group(7)),
            "best": float(match.group(8)),
            "wrst": float(match.group(9)),
            "stdev": float(match.group(10)),
        }
        for line in result.split("\n")
        if (match := pattern.match(line))
    ]


def path_analysis(host, current, previous) -> None:
    previous_path = hop_list(previous)
    current_path = hop_list(current)

    # Comprobar si hay cambios en el path
    is_path_changed = len(previous_path) != len(current_path)
    is_loss_increased = current_path[-1]["loss"] > LOSS
    is_rtt_increased = current_path[-1]["avg"] > RTT
    is_connection_lost = current_path[-1]["loss"] == 100

    if is_connection_lost:
        send_message(f"Se perdió la conexión con {host}"
                     f"\n\n{current}")
    elif is_path_changed or is_loss_increased or is_rtt_increased:
        check_for_changes(host, current, current_path, previous_path)


def check_for_changes(host, current, current_path, previous_path):
    for prev_hop, curr_hop in zip(previous_path, current_path):
        if prev_hop["host"] != curr_hop["host"]:
            print_change(current, None, "path", host, curr_hop, prev_hop, "host")
            return
        elif (prev_hop["loss"] * VARIATION) < curr_hop["loss"] and current_path[-1].get(
            "loss"
        ) > LOSS:
            print_change(
                current,
                current_path[-1].get("loss"),
                "pérdida de paquetes",
                host,
                curr_hop,
                prev_hop,
                "loss",
            )
            return
        elif (prev_hop["avg"] * VARIATION) < curr_hop["avg"] and current_path[-1].get(
            "avg"
        ) > RTT:
            print_change(
                current,
                current_path[-1].get("avg"),
                "tiempo de respuesta",
                host,
                curr_hop,
                prev_hop,
                "avg",
            )
            return


def print_change(current, stats, change_type, host, curr_hop, prev_hop, key):
    current_val = curr_hop[key]
    previous_val = prev_hop[key]
    hop_num = curr_hop["hop"]

    if key in ["avg", "loss"]:
        metric = "ms" if key == "avg" else "%"
        message = (
            f"Se presentó un cambio en el {change_type} hacia {host} ahora es de {stats}{metric} "
            f"se identifica el fallo en el hop #{hop_num} \nSalto IP {curr_hop['host']}: "
            f"Medición anterior {previous_val}{metric} --> Medición actual {current_val}{metric}"
            f"\n\n{current}"
        )
    else:
        message = (
            f"Se presentó un recálculo en el {change_type} hacia {host} en el hop #{hop_num} "
            f"\nSalto IP {curr_hop['host']}: IP anterior {previous_val} --> IP actual {current_val}"
            f"\n\n{current}"
        )

    response = send_message(message)
    print(response)


if __name__ == "__main__":
    previous_results = {host: None for host in HOSTS}

    while True:
        for host in HOSTS:
            current_result = mtr_result(host)
            if current_result:
                previous_result = previous_results[host]
                if previous_result is None:
                    previous_results[host] = current_result
                else:
                    if previous_result != current_result:
                        path_analysis(host, current_result, previous_result)
                        previous_results[host] = current_result
                    else:
                        print(
                            f"No hay diferencia para el host {host} entre el último y el actual resultado"
                        )
        time.sleep(60)
