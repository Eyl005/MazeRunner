def foo(ys: str):
    for y in ys:
        if y in "aeiou":
            return True
        elif y not in "aeiou":
            return False
    return -1
print(True or 1/0)