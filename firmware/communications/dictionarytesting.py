import json

def read_json():
    try:
        with open('commands.json','r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
        print("Data could not be loaded")
    return data



json_file = read_json()

print(json_file)


