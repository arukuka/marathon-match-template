import math
import argparse


# Ackley function
def calc(xs: list[float]) -> float:
    lhs_exp = 0.0
    for x in xs:
        lhs_exp += x ** 2
    lhs_exp = math.exp(-0.2 * math.sqrt(lhs_exp / len(xs)))

    rhs_exp = 0.0
    for x in xs:
        rhs_exp += math.cos(2 * math.pi * x)
    rhs_exp = math.exp(rhs_exp / len(xs))

    return 20 - 20 * lhs_exp + math.e - rhs_exp


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument('input')  # unused
    parser.add_argument('output')

    args = parser.parse_args()

    xs: list[float] = []
    with open(args.output, 'r') as ifp:
        xs = list(map(float, ifp.read().split()))

    print(f"Score = {calc(xs)}")


if __name__ == "__main__":
    main()
