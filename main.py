import subprocess
import time
import re

HOSTS = ["8.8.8.8", "129.213.76.17"]
RTT = 16
LOSS = 1

def mtr_result(host) -> str:
    try:
        mtr = subprocess.Popen(["mtr", "-r", "-c", "1", host], stdout=subprocess.PIPE)
        mtr.wait()
        return mtr.stdout.read().decode("utf-8")
    except Exception as e:
        print(e)
        return ""


def hop_list(result) -> list:
    pattern = (
        r"\s*(\d{1,2})\.\|--\s+([^\s]+)\s+(\d+(\.\d+)?)%?\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+(["
        r"\d\.]+)\s+([\d\.]+)"
    )

    hops = []
    for line in result.split("\n"):
        match = re.match(pattern, line)
        if match:
            hop_stats = {
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
            hops.append(hop_stats)

    return hops


def path_analysis(host, current, previous) -> None:
    previous_path = hop_list(previous)
    current_path = hop_list(current)

    # Comprobar la longitud de los caminos y la pérdida de paquetes en el último hop
    if len(previous_path) != len(current_path) or current_path[-1]["loss"] > LOSS:
        handle_path_change(host, current_path, previous_path, current)
        return

    # Comprobar el tiempo de respuesta en el último hop
    if current_path[-1]["avg"] > RTT:
        for prev_hop, curr_hop in zip(previous_path, current_path):
            if (prev_hop["avg"]*1.3) < curr_hop["avg"]:
                stats = f"{current_path[-1].get('avg')}ms hacia el host {host}"
                print_change(stats, "tiempo de respuesta", curr_hop, prev_hop, "avg", "ms")
                return


def handle_path_change(host, current_path, previous_path, current):
    if current_path[-1]["loss"] == 100.0:
        print(
            f"Se presenta falla en el path: destino inalcanzable host {host} no responde"
            f'\n{current}'
        )
    else:
        for prev_hop, curr_hop in zip(previous_path, current_path):
            if prev_hop["host"] != curr_hop["host"]:
                print_change(None, "path", curr_hop, prev_hop, "host", None)
                return
            if prev_hop["loss"] < curr_hop["loss"]:
                stats = f"{current_path[-1].get('loss')}% hacia el host {host}"
                print_change(stats, "pérdida de paquetes", curr_hop, prev_hop, "loss", "%")
                return


def print_change(stats, tipo_cambio, curr_hop, prev_hop, key, metric):
    if stats is not None:
        print(
            f'Se presentó un cambio en el {tipo_cambio} ahora es de {stats} '
            f'se identifica el fallo en el hop #{curr_hop["hop"]} '
            f'\nSalto IP {curr_hop["host"]}: Medición anterior {prev_hop[key]}{metric} --> Medición actual {curr_hop[key]}{metric}'
        )
    else:
        print(
            f'Se presentó un cambio en el {tipo_cambio} en el hop #{curr_hop["hop"]} '
            f'\nSalto IP {curr_hop["host"]}: IP anterior {prev_hop[key]} --> IP actual {curr_hop[key]}'
        )


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
                        print(f"No hay diferencia para el host {host} entre el último y el actual resultado")
        time.sleep(60)