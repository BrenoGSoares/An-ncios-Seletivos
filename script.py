
data_file = "BrenoGSoares/An-ncios-Seletivos/saida_rib.20181201.0800.txt"
print(data_file)

with open(data_file, 'r') as arq:
    linhas = arq.readlines()
    for linha in linhas:
        print(linha)