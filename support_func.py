import csv

def save_to_csv(data, filename):
    if not data:
        print(f"No data to save for {filename}.")
        return

    fieldnames = data[0].keys()
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def read_ids_from_txt(file_path):
    ids = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:  
                ids.append(line)
    return ids