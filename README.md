# prerequisite

- CMake
- Boost (header only)
- Python 3
- Docker
- Docker Compose V2

optional

- clangd
- clang-format

# 使い方

## 仮想環境の作成と有効化

ホストの環境を汚したくない場合は仮想環境の利用をご検討ください。

```console
$ python3 -m venv venv
$ .\venv\Scripts\Activate.ps1  # Windows の場合
$ pip install -r requirements.txt
```

## CMake プロジェクトの構成 / ビルド

自分は [Visual Studio Code の拡張機能: Cmake Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools) を用いています。

```console
$ mkdir -p build
$ cd build
$ cmake ..
...
$ cmake --build .
[2/2] Linking CXX executable main.exe
```

初期状態のプログラムは入力されたパラメータをそのまま出力するものになっています。

## コンテナ立ち上げ

以下のコマンドでデータベースインスタンスと optuna dashboard を立ち上げます。また、Optuna 用のデータベースとテーブルを作成するコンテナが走ります。

```console
$ docker compose up
[+] Running 4/0
 ✔ Container postgres                 Created
 ✔ Container postgres-client-job      Created
 ✔ Container optuna-dashboard         Created
 ✔ Container optuna-create-study-job  Created
Attaching to optuna-create-study-job, optuna-dashboard, postgres, postgres-client-job
postgres                 | 
postgres                 | PostgreSQL Database directory appears to contain a database; Skipping initialization
postgres                 |
...
```

停止するには Ctrl+C を押下して SIGINT を送ります。

## パラメーター探索

`study.py` スクリプトを用いてパラメータの探索を行います。

```console
$ python ./study.py --executable <ソルバーの実行ファイル> --judge <ジャッジのコマンド>
```

サンプルとして `judge.py` スクリプトを用意しました。入力のパラメータから Ackley function の計算を行い、AHC 形式の出力をするスクリプトになります。こちらを用いた場合、全体のコマンドは以下のようになります。

```console
$ python .\study.py --executable .\build\main.exe --judge python judge.py --n-trials 100
...
[I 2024-01-31 16:58:57,554] Trial 148 finished with value: 19.0 and parameters: {'x0': -1.7319821687918064, 'x1': -2.1314852775880055, 'x2': 6.525313064938267, 'x3': 6.222260313120273, 'x4': -10.513674156793138, 'x5': 16.332209099711143, 'x6': 2.1198913585357966, 'x7': 15.096331536512897, 'x8': 18.15230558883763, 'x9': -2.2737220920278776}. Best is trial 104 with value: 17.0.
num_iters=1, move_ave=0 [ms], time_spent=6 [ms]
ret=0
ret=0
output=Score = 17.853873707331886
...
```

`docker-compose.yaml` には optuna dashboard のコンテナも含まれており、http://localhost:8080 から学習の経過を確認することができます。

## データ削除

使用することがなくなったり、探索をやり直したくなったりしたら docker volume の削除を行うことで、最初の状態に戻します。

```console
$ docker compose down -v
```
