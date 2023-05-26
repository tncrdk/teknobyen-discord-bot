a = "navn til navn\nsitat\n\n  navn til navn\nsitat\n\n  "
a = a.strip().split("\n\n")
print(a)
a = list(map(str.strip, a))
print(a)
