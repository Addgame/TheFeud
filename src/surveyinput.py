import json

import os

name = input("Enter survey name: ")

survey_data = []
counter = 1

print("Press enter at any response name to end.")

while True:
    response = input("Enter response number " + str(counter) + ": ")
    if response == "":
        break
    number = int(input("Enter the count for response number " + str(counter) + ": "))
    survey_data.append({response: number})
    counter += 1

filename = "data/" + name + ".json"
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, 'w') as file:
    json.dump(survey_data, file)
