def function_one(arg_one: str, arg_two: int) -> int | str:
    print("this is certainly a test")

    c = 0
    for i in range(arg_two):
        c += len(arg_one)

    return c
