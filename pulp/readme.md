# PuLP

## document
https://coin-or.github.io/pulp/

## samples

* pulp

 https://qiita.com/SaitoTsutomu/items/070ca9cb37c6b2b492f0
 https://docs.pyq.jp/python/math_opt/pulp.html
 https://yamakuramun.info/2020/09/27/227/

* pandas

 https://pppurple.hatenablog.com/entry/2016/06/27/022310

## 基本設計

### 初期化

INPUT:
* 開発見積書 ひな形 [xlsm]
* 見積実績報告書 [xlsx]
* 要件(外)-工程-見積工数
* PJ情報（成果物、作業内容、外部委託有無） [txt]

PROCESS:
* read 見積実績報告書 *(openpyxl)*
* load Data *(Pandas)*
* edit 要件名Map

OUTPUT:
* 開発見積書 [xlsm]
* 要件名Map [txt]
* 要件(外) [1..*] --> [1] 要件(内)
* 外部見積 [memory]: 要件(内)―工程-見積工数

### 開発見積書 初期シート作成 [Manual]

INPUT:
* 開発見積書 [xlsm]

PROCESS:
* 開発見積シート生成、作業原価取得、営業見積シート生成 *(VBA Macro)*

OUTPUT:
* 開発見積書 [xlsm]
* 営業見積シート、開発見積シート、作業原価、

### 営業見積 算出

INPUT:
* 開発見積書 [xlsm]
* 見積実績報告書 [xlsx]
* 要件名Map [txt]
* 工程―等級別―配分(営業) [txt] *default*

PROCESS:
* read 見積実績報告書: *(openpyxl)*
* append 要件名Map
* 工数配分算出 *(PuLP)*
* write 営業見積 -> 開発見積書 *(Pandas)*

OUTPUT:
* 開発見積書: 営業見積 [xlsm]

### 開発見積 算出

INPUT:
* 開発見積書 [xlsm]
* 工程―等級別―配分(開発) [txt] *default*
* 営業-開発変換係数 [float]
* 目標粗利率 [float]

PROCESS:
* read 開発見積書: 営業見積 *(openpyxl)*
* 開発工数算出 *(PuLP)*
* write 開発見積書: 開発見積 *(Pandas)*
* save Parameters: 営業―開発変換係数, 目標粗利率

OUTPUT:
* 開発見積書: 開発見積 [xlsm]
* Parameters: 営業―開発変換係数, 目標粗利率 [txt]

### [外部委託] 外部委託工数 入力

INPUT:
* 開発見積書 [xlsm]

PROCESS:
* edit 開発見積書: 営業見積、外部委託工数 *(EXCEL)*

OUTPUT:
* 開発見積書書: 営業見積、外部委託工数 [xlsm]

### [外部委託] 開発見積 算出

参照=> [[開発見積 算出]]

