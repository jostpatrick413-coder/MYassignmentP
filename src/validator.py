# src/validator.py —— 校验器：把"人写的合法性谓词"接进数据流水线（生成器保证形状，校验器保证真值）
import importlib.util   # 动态加载三件套所在：包 → 子模块（必须写全 util——包不会自动加载子模块）

class InputValidator:
    def __init__(self, script_path, max_tries=20):
        self.script_path = script_path
        self.max_tries = max_tries   # 每组数据最多重造几次（默认 20）
        self.broken = False          # 校验器自身出错后置 True：只警告一次，之后一律放行
        self.func = None
        self._load()

    def _load(self):
        # 动态加载用户脚本：import 按"模块名"找文件，这里按"路径"直接加载（文件名不必是合法标识符）
        try:
            # 第 1 步：造"规格书"（ModuleSpec）——只登记三件事，不读文件、不执行：
            #   模块名 "user_validator"（内部名字，随便起，不靠它找文件）、货源路径 self.script_path
            #   （命令行 --validator 给的，就是 spec.origin）、搬运工类型 loader（.py 文件 = SourceFileLoader）
            spec = importlib.util.spec_from_file_location("user_validator", self.script_path)
            # 第 2 步：按规格书造"空盒子"——一个 ModuleType 对象，本质是空字典（__name__ 等标签已贴好）
            module = importlib.util.module_from_spec(spec)
            # 第 3 步：搬运工把文件执行进盒子，内部等价 exec(compile(源码, 路径, 'exec'), module.__dict__)；
            #   def 在这里只"打包"函数对象、函数体一行不跑——所以函数体带雷（1/0）要等调用时才炸
            spec.loader.exec_module(module)
        except Exception as e:
            self.broken = True
            print(f"[警告] 校验器脚本加载失败（{type(e).__name__}: {e}），本轮不校验、数据照常生成")
            return
        # 盒子装好了，查"货"在不在：hasattr = 查 module.__dict__ 里有没有 "is_valid" 这个键
        if not hasattr(module, "is_valid"):
            self.broken = True
            print(f"[警告] {self.script_path} 里没有 is_valid 函数，本轮不校验、数据照常生成")
            return
        self.func = module.is_valid   # 转交：函数对象挂到实例属性上，之后 validate() 只认 self.func，模块对象可丢弃

    def validate(self, input_str):
        # 契约：True = 合法放行；False = 重造。校验器自身报错/乱返回：警告一次后一律放行
        if self.broken:
            return True   # 保险丝已烧断（加载失败/上次调用炸过）：直接放行，再也不碰用户代码
        try:
            # 唯一真正调用用户 is_valid 的地方；input_str 与稍后喂给子进程的是同一份文本——
            # 校验器在"待测代码即将读到的真实输入"上审约束
            result = self.func(input_str)
        except Exception as e:
            self.broken = True   # 调用时炸（如函数体 1/0）：烧保险丝，从下次起直接放行
            print(f"[警告] 校验器自身报错（{type(e).__name__}: {e}），改为不校验、数据照常生成")
            return True          # 本次也放行——诊断失败不能让测试停摆
        if result is not True and result is not False:
            # 契约检查：必须严格是布尔值本身（is 不是 !=），1/0/"yes" 这类"假布尔"都算违约
            self.broken = True
            print(f"[警告] is_valid 应返回 True/False，收到 {result!r}，改为不校验、数据照常生成")
            return True
        return result   # 干净的 True/False 原样上交：主循环据此决定"开测"还是"重造"
# ==== 学习笔记（本文件全解，精简版）====
# 【为什么要有校验器】生成器只知道"形状"（几行几列、什么范围），不知道"题意"（这题要求数组
#   严格递增、要求图连通……）。合法性是题目的语义，机器猜不出来——所以由人写成谓词接进来：
#   生成器保证形状，校验器保证真值。Codeforces 出题人标配的 generator+validator 就是这套分工。
# 【importlib 动态加载】平时的 import 是按"模块名"去搜索路径里找；这里用户给的是任意路径，
#   文件名甚至不是合法标识符。spec_from_file_location(名字, 路径) 造"规格书"，
#   module_from_spec 按规格书造空模块，spec.loader.exec_module 把文件执行进去——三步等于
#   手工模拟了一遍 import 的加载流程。
# 【hasattr 探路】hasattr(module, "is_valid") 问"这个模块里有没有 is_valid"——防用户函数名写错
#   或根本没写，提前给出友好警告而不是等调用时炸 AttributeError。
# 【broken 一次性放行】校验器是"加分项"，绝不能因为它坏掉把整个测试器拖垮：任何异常
#   （加载失败/运行报错/乱返回值）都置 broken=True 并警告一次，之后 validate 一律放行。
#   诊断可以失败，主流程不能陪葬。
# 【is not True and is not False】校验返回值要用 is 而不是 !=：必须严格是布尔值本身，
#   1/0/"yes" 这类"假布尔"都算违约——契约明确，错误才能尽早暴露。
# ==== 学习笔记（多类题目适配，本轮新增，精简版）====
# 【万能接口】is_valid(输入文本) → True/False 是唯一契约：任何题目的约束都能翻译成 Python 谓词，
#   换题 = 换一个校验器文件，生成器一行不动。四类实例（会话目录有演示脚本）：
#   值域（全数 ≤50）、关系（三角形不等式 a+b>c）、序（严格递增）、形状（每行列数相同 = 矩形）。
# 【校验器看到的 = 待测代码看到的】validate 收到的 input_str 与喂给子进程的是同一份字符串——
#   校验器在"真实输入"上审约束，不是在一个抽象数据上审。
# 【只过滤不生产】校验器能筛掉不合法的，造不出新结构：首行参数模式（"第一行 N，接着 N 个数"）
#   这类生成器还不会造的数据，校验器只能全部拒绝 → 冲突报告。validator 与 generator 是配合关系。
# 【概率视角】每次重造独立掷骰，命中率 p，20 次全败概率 (1-p)^20：约束越紧、样例越大，
#   冲突跳过越常见——这是概率的诚实坦白，不是 bug；命中率太低就调生成器旋钮（范围/形状）。
# ==== 学习笔记（importlib 三步逐件拆，本轮新增，精简版）====
# 【模块本质 = 字典】模块就是名字空间，名字空间就是字典：module.is_valid 与
#   module.__dict__["is_valid"] 是同一个东西（is 判断为 True）。模块文件是"供货清单"：
#   执行文件代码，产生的函数/变量全装进这个字典。
# 【平时 import 藏着的三步】找到文件 → 造空字典当模块 → 执行文件装货。importlib 把机器拆开手动摇。
# 【第 1 步 spec_from_file_location】造"规格书"（ModuleSpec）：只登记三件事——模块名（name）、
#   货源路径（origin）、搬运工类型（loader，.py 文件是 SourceFileLoader）。不读文件、不执行。
# 【第 2 步 module_from_spec】按规格书造空盒子：ModuleType 对象，__name__ 等标签已贴好，货为空。
# 【第 3 步 exec_module】搬运工干活，内部等价于 exec(compile(源码, 路径, 'exec'), module.__dict__)：
#   def 也是语句，执行到 def 时函数对象落进盒子的字典。文件顶层所有东西（函数/变量/print）都在这步落地。
# 【def 只打包不执行】exec 执行到 def 时只把函数对象装进盒子，函数体一行都不跑——
#   所以"函数体带雷"（1/0）的文件加载不炸、调用才炸；"文件语法错"在加载（exec_module）时就炸。
#   两条故障路（加载失败 / 调用时报错）正是因此要分开处理，各自烧保险丝。
# 【为什么手动摇】import 只认模块名（搜 sys.path）；--validator 给的是任意路径、文件名不限，
#   没有"按路径一键导入"的公开接口——三步合体 = 手工版 import。
# ==== 学习笔记（点号语法拆解，本轮新增，精简版）====
# 【点 = 唯一的成员访问运算】importlib.util.spec_from_file_location 不是特殊语法，就是一路点下去：
#   包 → 子模块 → 函数；spec.loader.exec_module 同理：对象 → 属性（另一个对象）→ 方法。
#   每个点 = 查一次字典（模块的 __dict__ 或对象的），一切成员访问都长这样，与 args.seed 无异。
# 【模块也是对象】importlib.util 是模块套模块：包、子模块都是模块对象，函数是它的属性。
#   sys.modules 是所有已加载模块的登记簿（名字 → 模块对象）。
# 【包不自动加载子模块】import importlib 不会自动装 util——所以要用必须写 import importlib.util；
#   导入后子模块挂到包上成为属性（hasattr 从 False 变 True）。
# 【bound method 与 function】spec.loader.exec_module 是 bound method（self 已绑到 loader 实例），
#   spec_from_file_location 是普通 function（没有 self）。语法一样，差别只在点左边是实例还是模块。
#   方法查找会沿继承链往上找（exec_module 实为父类 _LoaderBasics 定义），但点号写法不变。
