from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import json
import re

# data_file = r"rib.20181201.0800..txt"
data_file = r"saida_rib.20181201.0800.txt"
processed_data = []


try:
    # reads the data from the file and transforms it into a list of data
    with open(data_file, "r") as arq:
        lines = arq.readlines()
        for line in lines:
            try:
                line_elements = line.rstrip("\n").split("|")
                asn_elements = line_elements[2].split()
                line_elements[2] = asn_elements
                processed_data.append(line_elements[1:3])
            except IndexError:
                print(f"Error processing line: {line}. list of index.")

    # TODO: check the difference between ipv4 and ipv6
    def check_valid_asn(line):
        owner_asn = line[1][-1]
        if len(line[1]) == 1:
            # owner
            return None
        elif owner_asn == line[1][-2]:
            # "Prepending"
            for element in reversed(line[1]):
                if owner_asn != element:
                    line[1].index(element)
                    return [line[0], owner_asn, line[1][line[1].index(element)]]
        return [line[0], owner_asn, line[1][-2]]

    def neighbors(data):
        neighbors_dict = {}
        for route in data:
            prefix = route[0]
            owner = route[1]
            value = route[2]

            if owner not in neighbors_dict:
                neighbors_dict[owner] = {}

            if prefix not in neighbors_dict[owner]:
                neighbors_dict[owner][prefix] = []

            neighbors_dict[owner][prefix].append(value)

        return neighbors_dict

    def lists_equal(lst1, lst2):
        return set(lst1) == set(lst2)

    def prefix_asn(data):
        # 0 --> Not Using
        # 1 --> Probably Using
        # 2 --> Very Likely Using
        if len(data) == 1:
            return 0

        result = []
        for i in range(len(data) - 1):
            temporary_result = 1
            if lists_equal(data[i], data[i + 1]):
                if temporary_result != 2:
                    temporary_result = 0
            else:
                temporary_result = 2

                element_count = defaultdict(int)

                # Iterando sobre todas as sublistas e elementos para contar quantos prefixos cada vizinho consegue ver
                for sublist in data:
                    for element in sublist:
                        element_count[element] += 1

                # Convertendo o dicionário de contagem para uma lista de listas
                result = [[key, value] for key, value in element_count.items()]

        # Soma a quantidade de prefixos que cada vizinho ve
        # Ex [1, 10] --> 10 vixinhos observam um único prefixo
        # Ex [4, 1] --> 1 vizinho observa 4 prefixos
        if result:
            number = []
            contagem = Counter(sublista[1] for sublista in result)
            for value, frequency in contagem.items():
                number.append([value, frequency])
            # Se o maior numero de vizinhos tiver sendo anunciado para apenas 1 ou 2 prefixos assumo que muito provavelmente está usando ASN
            repeat_neighbors = max(number, key=lambda x: x[1])
            if repeat_neighbors[0] < 2 and len(data) > 2:
                temporary_result = 2
            else:
                temporary_result = 1

        return temporary_result

    def show_info(data):
        data_results = []
        for owner, inner_dict in data.items():
            set_seen_asns = []

            for prefix, values in inner_dict.items():
                seen_asns = set()

                # Verificar ASN repetidos
                for asn in values:
                    if not asn in seen_asns:
                        seen_asns.add(asn)

                seen_asns = list(seen_asns)
                set_seen_asns.append(seen_asns)
            data_results.append(prefix_asn(set_seen_asns))
        return data_results

    def plot_graph(data_ipv4, data_ipv6):
        contagem_ipv4 = [data_ipv4.count(0), data_ipv4.count(1), data_ipv4.count(2)]
        contagem_ipv6 = [data_ipv6.count(0), data_ipv6.count(1), data_ipv6.count(2)]
        fig, axs = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
        rotulos = ["Not Using", "Probably Using", "Very Likely Using"]
        bar_labels = ["red", "blue", "orange"]
        axs[0].bar(rotulos, contagem_ipv4, color=bar_labels)
        axs[1].bar(rotulos, contagem_ipv6, color=bar_labels)
        # axs[0].bar_label(data_ipv4, size=10, label_type="edge")

        # fig.("Inferencias")
        fig.suptitle("Uso dos ASNs")
        axs[0].set_ylabel("Quantidade")
        axs[1].set_ylabel("Quantidade")
        axs[0].legend(title="Probabilidade de Uso: IPv4")
        axs[1].legend(title="Probabilidade de Uso: IPv6")

        plt.show()

    def main():
        asn_ipv4 = []
        asn_ipv6 = []

        pattern = "^[A-Za-z0-9:/]*$"
        for route in processed_data:
            if bool(re.match(pattern, route[0])):
                asn_ipv6.append(check_valid_asn(route))
            else:
                asn_ipv4.append(check_valid_asn(route))
        valid_asn_ipv4 = list(filter(None, asn_ipv4))
        valid_asn_ipv6 = list(filter(None, asn_ipv6))
        plot_graph(
            show_info(neighbors(valid_asn_ipv4)), show_info(neighbors(valid_asn_ipv6))
        )

        # print(json.dumps(neighbors(valid_asn), indent=2))
        pass

    main()

except FileNotFoundError:
    print(f"Error: File '{data_file}' not found.")
except Exception as e:
    print(f"Unexpected error: {e}")
