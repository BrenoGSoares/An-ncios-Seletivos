from collections import Counter
import json

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

    def prefix_asn(data):
        # 0 --> Not Using
        # 1 --> Probably Using
        # 2 --> very Likely Using
        if len(data) == 1:
            return 0
        else:
            temporary_result = 1
            for i in range(len(data) - 1):
                if sorted(data[i]) == sorted(data[i + 1]):
                    temporary_result = 0
                else:
                    temporary_result = 1
                    break
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
        print(data_results)

    def main():
        asn = []
        for route in processed_data:
            asn.append(check_valid_asn(route))
        valid_asn = list(filter(None, asn))
        show_info(neighbors(valid_asn))
        # print(json.dumps(neighbors(valid_asn), indent=2))
        pass

    main()

except FileNotFoundError:
    print(f"Error: File '{data_file}' not found.")
except Exception as e:
    print(f"Unexpected error: {e}")
