from collections import Counter
import json
import matplotlib.pyplot as plt

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

    # check if its ipv4 or ipv6
    def check_ipv4_or_ipv6(prefix):
        if "." in prefix:
            return "IPv4"
        elif ":" in prefix:
            return "IPv6"
        else:
            return "Unknown"

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
        neighbors_dict = {"IPv4": {}, "IPv6": {}}
        for route in data:
            prefix = route[0]
            owner = route[1]
            value = route[2]

            ip_type = check_ipv4_or_ipv6(prefix)

            if owner not in neighbors_dict[ip_type]:
                neighbors_dict[ip_type][owner] = {}

            if prefix not in neighbors_dict[ip_type][owner]:
                neighbors_dict[ip_type][owner][prefix] = []

            neighbors_dict[ip_type][owner][prefix].append(value)

        return neighbors_dict

    def show_info(data):
        for ip_type, ip_type_dict in data.items():
            print(f"--- {ip_type} ---")
            for owner, inner_dict in ip_type_dict.items():
                neighbors = len([asn for values in inner_dict.values() for asn in values])
                unique_neighbors = len(
                    set.union(*[set(values) for values in inner_dict.values()])
                )
                print(
                    f"Owner: {owner} | Neighbors {neighbors} | Unique Neighbors: {unique_neighbors}"
                )

                percentages = []

                for prefix, values in inner_dict.items():
                    seen_asns = set()
                    repeated_asn_prefix = []

                    for asn in values:
                        if asn in seen_asns:
                            repeated_asn_prefix.append(asn)
                        else:
                            seen_asns.add(asn)

                    unique_percentage = (
                        (len(values) - len(repeated_asn_prefix)) / unique_neighbors
                    ) * 100

                    percentages.append(unique_percentage)

                    print(
                        f"  Prefix: {prefix} - {len(values)} ASN Use: {unique_percentage:.2f}% |"
                    )

                # create a bar chart for each ASN owner
                plt.bar(inner_dict.keys(), percentages, label=f"Owner: {owner}")

                # add labels and title to the chart
                plt.xlabel("Prefixo")
                plt.ylabel("Porcentagem de Vizinhos Únicos")
                plt.title(f"Porcentagem de Vizinhos Únicos para Owner: {owner}")
                plt.legend()
                plt.show()

    def main():
        asn = []
        for route in processed_data:
            asn.append(check_valid_asn(route))
        valid_asn = list(filter(None, asn))
        show_info(neighbors(valid_asn))
        # print(json.dumps(neighbors(valid_asn), indent=2))
        pass

except FileNotFoundError:
    print(f"Error: File '{data_file}' not found.")
except Exception as e:
    print(f"Unexpected error: {e}")