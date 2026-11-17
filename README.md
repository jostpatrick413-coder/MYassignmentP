# OJ 本地样例测试器（OJ Local Sample Tester）

面向大一计概学生自己的本地判题辅助工具：OJ 上 WA 了只有冷冰冰的提示、看不到输入数据；本地 IDE 有报错却没有极限样例。本项目让你在本地自动生成测试数据、运行自己的代码、捕获超时与运行时错误，不用再对着 WA 抓瞎。

## 一、项目背景与目标

- **面向谁**：正在上计算概论、被 OJ 判题困扰的同学（第一用户就是作者本人）。
- **解决什么问题**：OJ 判 WA 时看不到输入数据和报错细节；本地手造测试数据又慢又覆盖不到边界情况。
- **已完成功能（V1.2）**：
  1. 生成指定范围的随机整数数组；
  2. 自动生成 4 类边界用例：全相同、升序、降序、极值交替；
  3. 自动运行待测代码并计时，判定三类状态：正常完成 / RE（运行时错误）/ TLE（2 秒超时）；
  4. RE 时从 traceback 提取具体异常类型（如 ZeroDivisionError），报错信息全文打印；
  5. 一次批量跑多组用例，逐组打印输入、状态、耗时与输出；
  6. 复杂度分析：多档规模（N=300/1000/2000）计时、扣除子进程启动开销后估算增长幂次，预警 O(N²) 及以上的 TLE 风险；
  7. 命令行参数化（argparse）：`--code / --check / --brute / --pid / --n / --min / --max / --seed / --timeout / --analyze`，附免费 `--help` 说明书；
  8. 对拍（WA 检测，V1.2）：以"暴力解/AC 代码"当裁判，随机小样例双跑比对，输出不一致立刻报 WA 并给出出错输入与两边输出；
  9. 题号约定（约定优于配置）：`--pid 30012` 自动按约定定位待测代码 `<题号>.py` 与裁判 `solutions/<题号>.py`；
  10. 固定随机种子（`--seed`）：同一 seed 每次生成完全相同的随机数据——抓到的 WA 样例可随时复现、随时重跑。

## 二、课程知识与核心设计

- **数据结构**：用 `list` 存储数组数据；用 `dict` 把用例名映射到用例数据（`{"all_same": [...], ...}`），便于按名遍历和扩展。
- **进程隔离（关键设计）**：用 `subprocess` 启动一个独立 Python 进程运行待测代码，而不是直接 `import` 调用。取舍：直接调用更快，但被测评代码一旦死循环或崩溃，会把测试器一起拖垮；独立进程能通过**退出码**判定 RE、通过**超时**判定 TLE——OJ一般的体验（）
- **计时**：`time.time()` 在子进程运行前后取差值。
- **复杂度**：`generate_array` 与 `generate_edge_cases` 均为 O(n)；单组测试的额外开销为常数，耗时瓶颈在待测代码自身。
- **列表推导式**：`[random.randint(...) for _ in range(n)]` 一行生成随机数组，比 for 循环逐个 append 更简洁。
- **对拍（差分测试）**：同一份输入喂给两份代码——待测代码与"暴力解/AC 代码"裁判，逐字比对输出。裁判必须"笨但一定对"（把题意原封不动写成代码、放弃优化），且用小规模随机数据（暴力解才跑得动）；逐字比对字符串还能顺带抓出输出格式错误。
- **约定优于配置**：约定"按题号命名"（待测 `<题号>.py`、裁判 `solutions/<题号>.py`），命令行只传题号，程序按约定位置自动找文件。
- **伪随机与种子**：计算机没有真随机——random 的"随机数"由固定公式（梅森旋转）与内部状态一步步算出，整串序列完全由起始状态（种子）决定。不设种子：系统自动挑开局，每次不同；设了种子（`random.seed`）：每次序列完全一致，抓到的 WA 样例才能复现。种子只固定"数据流"，不固定耗时——耗时是墙钟时间，本就每次不同。

## 三、安装与运行

- **环境**：Python 3.x。只使用标准库 `random` / `subprocess` / `time` / `sys` / `os` / `math` / `argparse`，无任何第三方依赖。
- **启动**：在项目根目录执行

  ```bash
  python main.py                                        # 默认：常规 5 组用例 + 复杂度分析
  python main.py --code 你的代码.py --no-analyze          # 测任意代码，跳过分析
  python main.py --check --code examples/demo_wa.py      # 对拍：坏代码立刻现形
  python main.py --check --pid 30012                     # 题号约定：自动找 solutions/30012.py 当裁判
  python main.py --code examples/demo_tle.py --timeout 1.0   # 自定义超时阈值
  python main.py --seed 42                                 # 固定随机种子：出错样例可复现
  python main.py --help                                  # 参数说明书
  ```

- **项目结构**：

  ```text
  AssignmentP/
  ├── main.py               # 程序入口：参数解析 → 生成数据 → 运行/对拍 → 复杂度分析
  ├── src/
  │   ├── __init__.py       # 空文件，标记 src 是 Python 包
  │   ├── generator.py      # 数据生成器（DataGenerator 类）
  │   ├── runner.py         # 代码运行器（CodeRunner 类 + RE 类型提取）
  │   ├── analyzer.py       # 复杂度分析器（ComplexityAnalyzer 类）
  │   └── checker.py        # 对拍器（Comparator 类，WA 检测）
  ├── docs/
  │   └── screenshot.png    # 运行截图
  ├── examples/
  │   ├── demo_solution.py  # 示例"待测代码"（求平均值，O(N)）
  │   ├── demo_rte.py       # 故意除零的坏代码（验证 RE 判定）
  │   ├── demo_tle.py       # 故意死循环的坏代码（验证 TLE 判定）
  │   ├── demo_n2.py        # 故意 O(N²) 的坏代码（验证复杂度分析）
  │   └── demo_wa.py        # 故意算错的坏代码（验证对拍抓 WA）
  ├── solutions/            # 本地 AC 题库（约定：文件名 = 题号；已 gitignore，不入库）
  └── README.md
  ```

- **自定义测试**：数据规模 `--n`、范围 `--min/--max`、随机种子 `--seed`、超时 `--timeout`、待测代码 `--code`、对拍 `--check` 全部命令行可调；`--pid 题号` 走题号约定（待测 `<题号>.py`，裁判 `solutions/<题号>.py`）；`--help` 查看全部参数。

## 四、功能展示

![运行截图](docs/screenshot.png)

示例输出（N=10，范围 1~100）：

```text
=== OJ 本地样例测试器 (v1.0) ===

--- 正在测试: all_same ---
输入数据: 1 1 1 1 1 1 1 1 1 1
[通过] 耗时: 0.0456s
程序输出: 1

--- 正在测试: already_sorted ---
输入数据: 1 2 3 4 5 6 7 8 9 10
[通过] 耗时: 0.0304s
程序输出: 5

--- 正在测试: reverse_sorted ---
输入数据: 10 9 8 7 6 5 4 3 2 1
[通过] 耗时: 0.0302s
程序输出: 5

--- 正在测试: extreme_values ---
输入数据: 1 100 1 100 1 100 1 100 1 100
[通过] 耗时: 0.0303s
程序输出: 50

--- 正在测试: random_case ---
输入数据: 41 41 79 60 74 33 11 9 85 13
[通过] 耗时: 0.0299s
程序输出: 44
```

RE 检测示例（`python main.py examples/demo_rte.py`，故意除零）：

```text
--- 正在测试: all_same ---
输入数据: 1 1 1 1 1 1 1 1 1 1
[运行时错误] ZeroDivisionError  耗时: 0.0726s
报错信息: Traceback (most recent call last):
  ...
ZeroDivisionError: integer division or modulo by zero
```

复杂度分析示例（`python main.py examples/demo_n2.py`，O(N²) 代码）：

```text
=== 复杂度分析 ===
  N=300    耗时: 0.0349s → 扣基线后 0.0029s
  N=1000   耗时: 0.0531s → 扣基线后 0.0211s
  N=2000   耗时: 0.1111s → 扣基线后 0.0791s
  相邻档位增长幂次: [1.66, 1.91]
  结论: 大致 O(N^2)，规模翻倍耗时约翻 4 倍，注意 TLE 风险
```

对拍示例（`python main.py --check --code examples/demo_wa.py`，坏代码 vs 默认裁判 demo_solution）：

```text
=== 对拍模式 (WA 检测) ===
待测代码: examples/demo_wa.py
暴力解(裁判): examples/demo_solution.py
随机样例: 10 组，每组 N=5

[WA] 第 1 组就抓到了！
输入数据: 15 15 12 74 61
暴力解输出(期望): 35
待测代码输出(实际): 44
```

固定随机种子示例（`python main.py --seed 42` 连跑两次，random_case 输入逐字一致；耗时行因墙钟噪声每次不同，但数据行完全一致）：

```text
第 1 次: 输入数据: 82 15 4 95 36 32 29 18 95 14
第 2 次: 输入数据: 82 15 4 95 36 32 29 18 95 14
```

## 五、测试与结果

5 组用例（N=10，范围 1~100）实测，平均值（取整）均与手算一致：

| 用例 | 数据 | 期望输出 | 实际输出 | 结果 |
| :--- | :--- | :--- | :--- | :--- |
| all_same | 10 个 1 | 1 | 1 | ✓ |
| already_sorted | 1~10 | 5 | 5 | ✓ |
| reverse_sorted | 10~1 | 5 | 5 | ✓ |
| extreme_values | 1、100 交替 | 50 | 50 | ✓ |
| random_case | 随机数组 | 手算 44 | 44 | ✓ |

边界说明：demo 对空输入有防御分支（直接返回，不崩溃）。RE 与 TLE 判定路径已用真实坏代码实测：demo_rte.py（故意除零）5 组用例全部判为 RE 并正确提取 ZeroDivisionError；demo_tle.py（故意死循环）5 组用例全部超时判为 TLE（阈值经 `--timeout` 可调，实测 1.0s 生效）。

对拍实测（20 组随机小样例，N=5）：

| 场景 | 待测 | 裁判 | 结果 |
| :--- | :--- | :--- | :--- |
| 抓 WA | demo_wa.py（分母 n-1） | demo_solution.py | 第 1 组即报 WA，输入与两边输出全部指出 ✓ |
| 通过 | demo_solution.py | demo_solution.py | 20 组全部一致 ✓ |
| 题号自动定位 | demo_wa.py | `--pid 30012` → solutions/30012.py | 自动找到裁判并抓出 WA ✓ |
| 缺裁判 | 任意 | `--pid 99999` | 友好提示"先存 AC 代码"，不闷声报错 ✓ |

`--seed` 实测：`--seed 42` 连跑两次，5 组输入数据逐字一致（不同 seed 数据不同）；`seed=0` 亦合法且可复现（代码用 `is not None` 判断，防住"0 被当成未给"的陷阱）；对拍模式不打印耗时，同 seed 完整输出逐字一致。

## 六、局限与改进

- **对拍（WA 检测，V1.2）已完成，但定位是"机制验证 / 思路展示"**：真正投入使用需要持续积累 AC 题库（`solutions/`，每人本地自建、不入库），并需要为每题补充输入格式描述——目前只覆盖"一行整数数组"类题型，多行、多组、字符串等题型待扩展。
- 尚无输出格式的专项检测（对拍逐字比对可顺带抓格式差异）。
- 复杂度分析雏形已实现（N=300/1000/2000 三档计时、扣除启动开销后估算增长幂次）；内存监控（MLE）仍待 V1.5/V2.0。
- 参数化已用 argparse 完成（`--code / --check / --brute / --pid / --n / --min / --max / --seed / --timeout / --analyze`）。
- 已添加 .gitignore 排除 `__pycache__` 缓存与 `solutions/` 本地题库（公开仓库不放题解，避免学术诚信问题）。

## 七、来源与 AI 使用声明

```text
使用工具：DeepSeek（对话式 AI，生成 V1.0 初版代码框架）；Qoder（本地编程 Agent，用于代码讲解、修改与调试）
参与环节：需求拆解、项目结构设计、生成 generator / runner / main / 示例代码初稿、本文档草稿
本人完成的设计、修改与判断：
  · 选题与需求定义（OJ 本地样例测试器）；
  .每个小功能末以#附上自己的收获与理解
验证方法及结果：Python 语法检查通过；运行 python main.py 得到 5 组用例结果，与手算期望值一致；RE/TLE 判定路径已用坏代码（demo_rte.py / demo_tle.py）实测通过；复杂度分析器经 O(N²) 代码（demo_n2.py）验证可正确预警；对拍经坏代码（demo_wa.py，分母 n-1）实测：第 1 组随机样例即报 WA 并给出输入与两边输出；--pid 题号约定的自动定位/缺裁判提示两条路径均已实测；--seed 经实测：同 seed 两次运行输入数据逐字一致、seed=0 合法可复现、不同 seed 数据不同。
代表性协作案例或记录位置：DeepSeek 对话"大作业"；Qoder 会话开发记录。
引用与复用的外部资源：Python 标准库（random、subprocess、time、sys）；《课程大作业说明及评分标准》（Hongfei Yan，2026 fall）。
```
