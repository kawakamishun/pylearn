from pulp import *


# 数理モデル
model = LpProblem('sample', sense=LpMaximize)
# sense : 問題の種類, LpMinimize, LpMaximize

# 変数
x = LpVariable('x', lowBound=0)
# lowBound = 下限, upBound = 上限, cat = 変数の種類
# LpContinuous : 連続値, LpInteger : 整数値, LpBinary : バイナリ値
y = LpVariable('y', lowBound=0)

# 目的関数
model += 100 * x + 100 * y

# 制約条件
model += x + 2 * y <= 16
model += 3 * x + y <= 18

# ソルバー実行
model.solve()

# 結果
print(f'status={LpStatus.get(model.status)}', f'x={value(x)}', f'y={value(y)}')
