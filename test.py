a = []

match a:
    case [e, *d]:
        print(e)
        print(d)
    case []:
        print("Null")
