file = open("facts.txt", "r")

text = file.read()

file.close()


def get_names(text: str):
    splited = text.split("\n")
    names = []
    for i in range(0, len(splited)):
        if "Name = " in splited[i]:
            names.append(splited[i].split('=')[1])
    return  names


names = get_names(text)

print(names)