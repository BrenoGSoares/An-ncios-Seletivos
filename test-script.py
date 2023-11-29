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

    # TODO: check the difference between ipv4 and ipv6
    def check_valid_asn(line, threshold=80):
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
        
        # adding selective ads logic 
        unique_percentage = (
            (len(line[1]) - len(set(line[1]))) / len(set(line[1]))
        ) * 100
        if unique_percentage < threshold:
            return [line[0], owner_asn, "Selective Advertisement"]
        else:
            return [line[0], owner_asn, "Non-Selective Advertisement"]

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

    # generating graphs with matplotlib 
    def show_info(data):
        for owner, inner_dict in data.items():
            neighbors = len([asn for values in inner_dict.values() for asn in values])
            unique_neighbors = len(
                set.union(*[set(values) for values in inner_dict.values()])
            )
            print(
                f"Owner: {owner} | Neighbors {neighbors} | Unique Neighbors: {unique_neighbors}"
            )

            unique_percentages = [
                (len(values) - len(set(values))) / len(set(values)) * 100
                for values in inner_dict.values()
            ]

            # bar chart
            plt.bar(inner_dict.keys(), unique_percentages, label=f"Owner: {owner}")

            # display labels and title
            plt.xlabel("Prefix")
            plt.ylabel("Unique Neighbor Percentage")
            plt.title(f"Unique Neighbor Percentage for Owner: {owner}")
            plt.legend()
            plt.show()

    # adjustment of the Main Function
    def main(threshold=80):
        asn = []
        for route in processed_data:
            asn.append(check_valid_asn(route, threshold))
        valid_asn = list(filter(None, asn))
        neighbor_data = neighbors(valid_asn)
        show_info(neighbor_data)

except FileNotFoundError:
    print(f"Error: File '{data_file}' not found.")
except Exception as e:
    print(f"Unexpected error: {e}")