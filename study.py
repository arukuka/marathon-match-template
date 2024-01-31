import argparse
import pathlib
import functools
import tempfile
import json
import subprocess
import re
import itertools
import typing

import optuna


class Command:
    def __init__(self, cmd: list[str]):
        self.executable = pathlib.Path(cmd[0])
        self.args = cmd[1:]

    def __iter__(self):
        return itertools.chain.from_iterable([
                [str(self.executable.resolve())],
                self.args
            ])


T = typing.TypeVar('T')
U = typing.TypeVar('U')


def if_present(v: T | None, func: typing.Callable[[T], U]) -> U | None:
    if v is None:
        return None
    return func(v)


def objective(trial: optuna.Trial,
              executable: pathlib.Path,
              judge_executable: Command,
              temp_dir_root: str | None,
              input_format: str):
    xs = [trial.suggest_float("x" + str(i), -32.768, 32.768)
          for i in range(10)]

    score = 0

    with tempfile.TemporaryDirectory(dir=temp_dir_root) as dname:
        tdir = pathlib.Path(dname)

        json_file_path = tdir / 'param.json'
        json_data = {
            'xs': xs
        }
        with open(tdir / 'param.json', 'w') as fp:
            json.dump(json_data, fp)

        NUM_SEEDS = 1
        for step in range(NUM_SEEDS):

            solver_input_path = pathlib.Path(input_format.format(step))
            solver_output_path = tdir / f"{step}.out.txt"

            with open(solver_input_path, 'r') as ifp:
                with open(solver_output_path, 'w') as ofp:
                    solver_proc = subprocess.run(
                        [
                            executable.resolve(),
                            str(json_file_path.resolve()),
                        ],
                        stdin=ifp,
                        stdout=ofp,
                    )
                    print(f"ret={solver_proc.returncode}")

            judge_proc = subprocess.run(
                list(itertools.chain.from_iterable(
                    [
                        list(judge_executable),
                        [str(solver_input_path.resolve())],
                        [str(solver_output_path.resolve())],
                    ],
                )),
                stdout=subprocess.PIPE,
            )
            print(f"ret={solver_proc.returncode}")

            output = judge_proc.stdout.decode()
            print(f"output={output}")
            sub_score = int(re.findall(r'Score = (\d+)', output)[0])

            score += sub_score

            trial.report(score, step)
            if trial.should_prune():
                raise optuna.TrialPruned()

    return score


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-e', '--executable', type=pathlib.Path,
                        default=pathlib.Path('./build/main'))
    parser.add_argument('-j', '--judge', nargs='*',
                        default=['./tools/target/release/vis'])
    parser.add_argument(
        '-s', '--storage', type=str,
        default='postgresql://postgres:postgres@localhost:5432/db',
    )
    parser.add_argument('-n', '--study', type=str, default='study')
    parser.add_argument('-t', '--temp-dir', default=None)
    parser.add_argument('--n-trials', default=None)

    args = parser.parse_args()

    print(args.n_trials)

    study = optuna.load_study(
        study_name=args.study, storage=args.storage
    )
    study.optimize(functools.partial(
        objective,
        executable=args.executable,
        judge_executable=args.judge,
        temp_dir_root=args.temp_dir,
        input_format='./main.cpp',
    ), n_trials=if_present(args.n_trials, int))


if __name__ == "__main__":
    main()
