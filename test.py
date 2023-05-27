import re


a = "til og"
speaker = re.findall(r"\b(?!til|og)\b\w+", a)
print(speaker)
