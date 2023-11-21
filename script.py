data_file = r"saida_rib.20181201.0800.txt"

print(data_file)
processed_data = []
asn = []


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
            return None
        return [line[0], owner_asn, line[1][-2]]

    def neighbors(data):
        neighbors_dict = {}
        for route in data:
            owner = route[1]
            prefix = route[0]
            value = route[2]

            if owner not in neighbors_dict:
                neighbors_dict[owner] = []

            found = False
            for entry in neighbors_dict[owner]:
                if entry[0] == prefix:
                    entry[1].append(value)
                    found = True
                    break

            if not found:
                neighbors_dict[owner].append([prefix, [value]])

        neighbors_list = [[owner, entries] for owner, entries in neighbors_dict.items()]
        return neighbors_list

    def main():
        for route in processed_data:
            asn.append(check_valid_asn(route))
        valid_asn = list(filter(None, asn))
        print(neighbors(valid_asn))
        pass

    main()

except FileNotFoundError:
    print(f"Error: File '{data_file}' not found.")
except Exception as e:
    print(f"Unexpected error: {e}")
