# examples/demo_validator.py
# 校验器示例：只写一个 is_valid(输入文本) → True/False，测试器会自动导入并调用
# demo_solution 是"求平均数"题，它的真实约束只有两条：
#   1) 至少一个数（没有数就没有平均数）
#   2) 每个数都是整数（int() 转不动就崩）
# 返回 False 的输入会被测试器判"不合法"并自动重造（配 --rows 0-2 能看到空输入被拦下重掷）

def is_valid(input_str):
    if not input_str.strip():              # 空输入：不合法
        return False
    for token in input_str.split():        # 逐个数检查
        if not token.lstrip("-").isdigit():
            return False                   # 非整数：不合法
    return True                            # 全部过关：合法
