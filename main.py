import argparse
import sys

from src import optimizer, use_cases


def main(argv=None):
    p = argparse.ArgumentParser(
        description="PC build optimizer (0/1 knapsack DP per the MSML 606 proposal)."
    )
    p.add_argument("--budget", type=int, required=True,
                   help="Total budget in dollars (integer).")
    p.add_argument("--use-case", required=True, choices=use_cases.USE_CASES,
                   help="Which weighting profile to apply.")
    args = p.parse_args(argv)

    print(f"Running optimizer for use case '{args.use_case}', budget ${args.budget}...")
    build = optimizer.optimize(budget=args.budget, use_case=args.use_case)
    print(optimizer.format_build(build))
    return 0


if __name__ == "__main__":
    sys.exit(main())
