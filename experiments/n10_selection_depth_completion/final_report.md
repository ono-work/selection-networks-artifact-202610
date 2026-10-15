# n <= 10 selection-depth completion report

## 結論

リポジトリ内の既存成果物，構造関係，新規3判定を接続した結果，all 1 <= t <= n <= 10 are determined exactly と主張できる．機械検査ではexact 110セル，未確定0，整合性エラー0である．

## 定義と構造閉包

V型は先頭t本を昇順のt最小値にし，U型は順不同のt最小値集合にする．depthはmatching layer数である．使用した閉包規則はUDepth<=VDepth，n単調性，Vのt単調性，U(t,n)=U(n-t,n)，t=1境界，U(n,n)=0，V(n-1,n)=V(n,n)=sorting depth，n<=10の既知sorting depths，およびNakanoのt=2結果である．

追加実験前の独立なgapはV(2,7)=[4,5]，U(2,9)=[4,5]，V(2,9)=[5,6]の3件だった．U(7,9)はU-dualityにより独立jobではない．

## 新規job

| job | result | runtime (s) | consequence |
| --- | --- | ---: | --- |
| V_t2_n7_d4 | UNSAT | 0.431 | VDepth(2,7)=5 |
| U_t2_n9_d4 | UNSAT | 208.201 | UDepth(2,9)=UDepth(7,9)=5 |
| V_t2_n9_d5 | UNSAT | 1008.151 | VDepth(2,9)=6 |

3件はいずれもclingo 5.8.0の正常終了UNSATISFIABLEであり，TIMEOUT，UNKNOWN，ERRORは0件だった．instanceのn，t，depth fact，raw Result，decision statusを独立に照合した．

## 既存成果物の再監査

Milestone 3B smoke，baseline n=7，8，9，10，Nakano一次資料監査，sorting-depth境界，V(4,9) final certificateを使用した．既存SAT witness 53件をPython verifierで再実行し，合計10564個のBoolean入力を検査した．verifierはASP生成時のtarget encodingから独立であり，各layerのmatching条件も検査する．

特にVDepth(3,6)=5，UDepth(3,6)=3，UDepth(4,6)=4をraw結果とwitnessから再確認した．したがって会話上の候補UDepth(4,6)=3は誤りで，dualityによりUDepth(2,6)=4である．

VDepth(3,7)=6についてはdepth-5のraw UNSATISFIABLEとdepth-6 witnessを確認した．原稿のdepth-4 UNSATという一括記述だけでは不十分であり，これは修正対象である．

VDepth(4,9)=7のclosure certificateはcheckout名変更によりstrict byte hashが変化していたが，凍結bundleと現行JSONから旧／新絶対パスを同じrepository-root tokenへ正規化したSHA-256は一致した．depth-7 witnessは全512 Boolean入力で新たに検証した．

## Exact tables

## VDepth(t,n)

| n \\ t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | — | — | — | — | — | — | — | — | — |
| 2 | 1 | 1 | — | — | — | — | — | — | — | — |
| 3 | 2 | 3 | 3 | — | — | — | — | — | — | — |
| 4 | 2 | 3 | 3 | 3 | — | — | — | — | — | — |
| 5 | 3 | 4 | 5 | 5 | 5 | — | — | — | — | — |
| 6 | 3 | 4 | 5 | 5 | 5 | 5 | — | — | — | — |
| 7 | 3 | 5 | 6 | 6 | 6 | 6 | 6 | — | — | — |
| 8 | 3 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | — | — |
| 9 | 4 | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | — |
| 10 | 4 | 6 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |

## UDepth(t,n)

| n \\ t | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | — | — | — | — | — | — | — | — | — |
| 2 | 1 | 0 | — | — | — | — | — | — | — | — |
| 3 | 2 | 2 | 0 | — | — | — | — | — | — | — |
| 4 | 2 | 2 | 2 | 0 | — | — | — | — | — | — |
| 5 | 3 | 3 | 3 | 3 | 0 | — | — | — | — | — |
| 6 | 3 | 4 | 3 | 4 | 3 | 0 | — | — | — | — |
| 7 | 3 | 4 | 4 | 4 | 4 | 3 | 0 | — | — | — |
| 8 | 3 | 4 | 4 | 4 | 4 | 4 | 3 | 0 | — | — |
| 9 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 0 | — |
| 10 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 0 |

## 原稿との差分

3群の修正対象をmanuscript_discrepancies.jsonへ保存した．本作業ではmanuscript/main.texを編集していない．

## 再現方法

追加実験前のgap再構成：

    .venv/bin/python -m src.complete_n10_selection_depths --prepare

未実行jobだけを実行し各終了後に再閉包：

    .venv/bin/python -m src.complete_n10_selection_depths --run-all

既存結果から監査・表を再生成：

    .venv/bin/python -m src.complete_n10_selection_depths --generate

専用test：

    .venv/bin/python -m pytest tests/test_n10_selection_depth_completion.py -q

## 注意

実行時git treeはdirtyで，多数の既存untracked artifactを含む．commit hashだけでは今回の実行状態を復元できない．manifest.jsonに実行ソースのSHA-256とgit statusを保存した．solverの大規模分割探索は行っていない．

## Tests

全suiteは421 passed in 104.96s，専用・変更周辺suiteは28 passed in 1.59sだった．
