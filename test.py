def foo(a: str):
    return a

def parser(parser,arg, *args):
    return parser(arg, *args)

res = parser(foo, 3)
print(res)
