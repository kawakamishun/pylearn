from enum import Enum
import pandas as pd
from itertools import product
from pulp import *

"""

# 営業金額
e_sum = SUM(e_est * e_cost)
e_total = e_sum * 1.03

# 開発金額
d_sum = 
sum(d_est['要件A']['設計'][*] * d_rat['設計'][*] * d_cost[*]) +
sum(d_est['要件A']['実装'][*] * d_rat['実装'] * d_cost[*]) + 
sum(d_est['要件A']['テスト'][*] * d_rat['テスト'] * d_cost[*]) + 
sum(d_est['要件B']['評価対応'][*] * d_rat['評価対応'] * d_cost[*])

# 目標利益率
p_margin = 1 - (d_sum / e_sum) 

p_margin >= 0.37 and p_margin < 0.374


# DATA

# 営業
e_est = {
    '要件A' : {
        '設計' : {
            PM : 0.0,
            G4 : 2.0,
            G3 : 3.0,
            G2 : 1.0
        },
        '実装' : {
            PM : 0.0,
            G4 : 1.0,
            G3 : 3.0,
            G2 : 2.0
        },
        'テスト' : {
            PM : 0.0,
            G4 : 0.5,
            G3 : 3.0,
            G2 : 4.0
        },
    },

    "要件B" : {
        '評価対応' : {
            PM : 0.5,
            G4 : 1.0,
            G3 : 3.0,
            G2 : 2.0
        },
    }
}

# 変数

# 比率
RATIO = 1.31

# 開発 
d_est = {
    '要件A' : {
        '設計' : {
            PM : 0.0,
            G4 : 2.0,
            G3 : 3.0,
            G2 : 1.0
        },
        '実装' : {
            PM : 0.0,
            G4 : 1.0,
            G3 : 3.0,
            G2 : 2.0
        },
        'テスト' : {
            PM : 0.0,
            G4 : 0.5,
            G3 : 3.0,
            G2 : 4.0
        },
    },

    "要件B" : {
        '評価対応' : {
            PM : 0.5,
            G4 : 1.0,
            G3 : 3.0,
            G2 : 2.0
        },
    }
}

# 営業単価
e_cost = {
    PM : 100,
    G4 : 92,
    G3 : 87,
    G2 : 85,
    G1 : 82
}

# 開発単価
d_cost = {
    PM : 94,
    G4 : 85,
    G3 : 82,
    G2 : 80,
    G1 : 78
}
"""

class Ranks(Enum):
    PM = 'PM'
    G4 = 'G4'
    G3 = 'G3'
    G2 = 'G2'

    @classmethod
    def value_of(cls, value):
        for e in Ranks:
            if e.value == value:
                return e
        raise ValueError(f'invalid Ranks value: {value}')

class Phases(Enum):
    DSN = 'DSN'
    IMP = 'IMP'
    TST = 'TST'
    QA = 'QA'

    @classmethod
    def value_of(cls, value):
        for e in Phases:
            if e.value == value:
                return e
        raise ValueError(f'invalid Phases value: {value}')

# 外部入力データ
# 粗利率目標
margin_goal = 0.375

# 合計金額
total = 2576

# 営業―開発 算出係数
ratio = 1.28

# 開発単価
units = [87, 85, 82, 79]

# 見積工数
# 要件A
req_A = ['req_A', 6.5, 5.9, 6.8, 0.0]
# 要件B
req_B = ['req_B', 0.0, 0.0, 0.0, 10.0]
data = [req_A, req_B]

columns = ['NAME', 'DESIGN', 'IMPL', 'TEST', 'QA']
data_df = pd.DataFrame(data=data, columns=columns)
print(data_df)


# 数理モデル

model = LpProblem('sample', sense=LpMinimize)


# 変数

# 工程―等級別 工数配分
phase = [p.name for p in Phases]
ranks = [r.name for r in Ranks]
pr = itertools.product(phase, ranks)
var_df = pd.DataFrame(data=list(pr), columns=['PHASE', 'RANK'])
var_df['LBOUNDS'] = [0.1, 0.2, 0.4, 0.0] + [0.0, 0.15, 0.3, 0.15] + [0.0, 0.15, 0.2, 0.25] + [0.1, 0.2, 0.2, 0.15]
var_df['LBOUNDS'] = var_df.LBOUNDS / ratio
var_df['UBOUNDS'] = [0.15, 1.0, 1.0, 0.0] + [0.15, 1.0, 1.0, 0.3] + [0.1, 1.0, 1.0, 0.3] + [0.2, 1.0, 1.0, 0.3]
var_df['UBOUNDS'] = var_df.UBOUNDS / ratio

var_df.to_csv('vars.csv', index=False, encoding='utf-8')

# 外部ファイルから変数を読み込む
var_df = pd.read_csv('vars.csv', encoding='utf-8')
print(var_df)

dsn_vars = {Ranks.value_of(r): LpVariable(f'{p}_{r}', lowBound=lb, upBound=ub, cat=LpContinuous) for p, r, lb, ub \
            in zip(var_df.PHASE, var_df.RANK, var_df.LBOUNDS, var_df.UBOUNDS) if Phases.value_of(p) == Phases.DSN}
imp_vars = {Ranks.value_of(r): LpVariable(f'{p}_{r}', lowBound=lb, upBound=ub, cat=LpContinuous) for p, r, lb, ub \
            in zip(var_df.PHASE, var_df.RANK, var_df.LBOUNDS, var_df.UBOUNDS) if Phases.value_of(p) == Phases.IMP}
tst_vars = {Ranks.value_of(r): LpVariable(f'{p}_{r}', lowBound=lb, upBound=ub, cat=LpContinuous) for p, r, lb, ub \
            in zip(var_df.PHASE, var_df.RANK, var_df.LBOUNDS, var_df.UBOUNDS) if Phases.value_of(p) == Phases.TST}
qa_vars = {Ranks.value_of(r): LpVariable(f'{p}_{r}', lowBound=lb, upBound=ub, cat=LpContinuous) for p, r, lb, ub \
            in zip(var_df.PHASE, var_df.RANK, var_df.LBOUNDS, var_df.UBOUNDS) if Phases.value_of(p) == Phases.QA}


# 目的関数

# 開発見積金額 合計
total_k = (lpSum(data_df.DESIGN) * dsn_vars[Ranks.PM] * units[0] + 
            lpSum(data_df.DESIGN) * dsn_vars[Ranks.G4] * units[1] + 
            lpSum(data_df.DESIGN) * dsn_vars[Ranks.G3] * units[2] + 
            lpSum(data_df.DESIGN) * dsn_vars[Ranks.G2] * units[3] + 
            lpSum(data_df.IMPL) * imp_vars[Ranks.PM] * units[0] + 
            lpSum(data_df.IMPL) * imp_vars[Ranks.G4] * units[1] + 
            lpSum(data_df.IMPL) * imp_vars[Ranks.G3] * units[2] + 
            lpSum(data_df.IMPL) * imp_vars[Ranks.G2] * units[3] + 
            lpSum(data_df.TEST) * tst_vars[Ranks.PM] * units[0] + 
            lpSum(data_df.TEST) * tst_vars[Ranks.G4] * units[1] + 
            lpSum(data_df.TEST) * tst_vars[Ranks.G3] * units[2] + 
            lpSum(data_df.TEST) * tst_vars[Ranks.G2] * units[3] + 
            lpSum(data_df.QA) * qa_vars[Ranks.PM] * units[0] + 
            lpSum(data_df.QA) * qa_vars[Ranks.G4] * units[1] + 
            lpSum(data_df.QA) * qa_vars[Ranks.G3] * units[2] + 
            lpSum(data_df.QA) * qa_vars[Ranks.G2] * units[3])

# 目標粗利率との差異
model += margin_goal - (1 - (total_k / (total * 1.03)))


# 制約条件

model += total_k <= (total / ratio)
model += (dsn_vars[Ranks.PM] + dsn_vars[Ranks.G4] + dsn_vars[Ranks.G3] + dsn_vars[Ranks.G2] == 1.0 / ratio)
model += (imp_vars[Ranks.PM] + imp_vars[Ranks.G4] + imp_vars[Ranks.G3] + imp_vars[Ranks.G2] == 1.0 / ratio)
model += (tst_vars[Ranks.PM] + tst_vars[Ranks.G4] + tst_vars[Ranks.G3] + tst_vars[Ranks.G2] == 1.0 / ratio)
model += (qa_vars[Ranks.PM] + qa_vars[Ranks.G4] + qa_vars[Ranks.G3] + qa_vars[Ranks.G2] == 1.0 / ratio)


# ソルバー実行

model.solve()


# 結果

var_df['VAR'] = [value(var) for var in dsn_vars.values()] \
            + [value(var) for var in imp_vars.values()] \
            + [value(var) for var in tst_vars.values()] \
            + [value(var) for var in qa_vars.values()] \

# 実行結果
print(f'status={LpStatus.get(model.status)}')
#
print(f'objective={value(model.objective)}')
print(var_df)
