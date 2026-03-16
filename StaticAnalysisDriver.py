import ast
import copy
from typing import Dict, List, Tuple, Set

class StaticAnalysisDriver:
    """静态分析核心驱动类，负责代码的静态检测"""
    
    def __init__(self, code: str):
        self.code = code
        self.ast_tree = ast.parse(code)  # 生成AST抽象语法树
        self.issues: Dict[str, List[Tuple[int, str]]] = {
            "unused_variables": [],
            "duplicate_code": [],
            "inefficient_loops": [],
            "unnecessary_casts": []
        }

    def analyze_unused_variables(self) -> None:
        """分析未使用的变量（静态分析核心逻辑1）"""
        used_names = set()
        defined_names = set()

        # 遍历AST收集已定义和已使用的变量
        class NameVisitor(ast.NodeVisitor):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
                elif isinstance(node.ctx, ast.Store):
                    defined_names.add(node.id)
                self.generic_visit(node)

        NameVisitor().visit(self.ast_tree)
        
        # 找出未使用的变量
        unused = defined_names - used_names
        for var in unused:
            # 简化处理：定位变量定义行（实际场景需更精准的位置匹配）
            self.issues["unused_variables"].append((0, f"Unused variable: {var}"))

    def analyze_inefficient_loops(self) -> None:
        """分析低效循环（如在循环内重复计算）（静态分析核心逻辑2）"""
        class LoopVisitor(ast.NodeVisitor):
            def visit_For(self, node):
                # 检测循环内的列表拼接（低效操作，应改用列表append）
                for item in ast.walk(node):
                    if isinstance(item, ast.BinOp) and isinstance(item.op, ast.Add):
                        if isinstance(item.left, ast.List) or isinstance(item.right, ast.List):
                            self.issues["inefficient_loops"].append(
                                (node.lineno, "Inefficient list concatenation in loop (use append instead)")
                            )
                self.generic_visit(node)

        LoopVisitor().visit(self.ast_tree)

    def run_full_analysis(self) -> Dict[str, List[Tuple[int, str]]]:
        """运行全量静态分析"""
        self.analyze_unused_variables()
        self.analyze_inefficient_loops()
        # 可扩展：添加更多分析规则（如重复代码、不必要的类型转换）
        return self.issues

class CodeOptimizer:
    """代码优化器，基于静态分析结果生成优化代码"""
    
    def __init__(self, analysis_driver: StaticAnalysisDriver):
        self.driver = analysis_driver
        self.optimized_code = None

    def optimize_unused_variables(self, tree: ast.AST) -> ast.AST:
        """移除未使用的变量定义（自动优化逻辑1）"""
        # 复制AST避免修改原树
        new_tree = copy.deepcopy(tree)
        unused_vars = [issue[1].split(": ")[1] for issue in self.driver.issues["unused_variables"]]
        
        class UnusedVarRemover(ast.NodeTransformer):
            def visit_Assign(self, node):
                # 仅移除简单变量赋值（如 a = 1）
                if isinstance(node.targets[0], ast.Name) and node.targets[0].id in unused_vars:
                    return None  # 返回None表示删除该节点
                return self.generic_visit(node)

        return UnusedVarRemover().visit(new_tree)

    def optimize_loops(self, tree: ast.AST) -> ast.AST:
        """优化循环内的列表拼接（自动优化逻辑2）"""
        new_tree = copy.deepcopy(tree)
        
        class LoopOptimizer(ast.NodeTransformer):
            def visit_For(self, node):
                # 遍历循环内节点，替换列表拼接为append
                for idx, item in enumerate(node.body):
                    if isinstance(item, ast.Assign):
                        value = item.value
                        if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
                            if isinstance(value.left, ast.List) or isinstance(value.right, ast.List):
                                # 示例：将 a = a + [1] 改为 a.append(1)
                                target = item.targets[0]
                                append_call = ast.Call(
                                    func=ast.Attribute(value=target, attr="append", ctx=ast.Load()),
                                    args=[value.right.elts[0] if isinstance(value.right, ast.List) else value.left.elts[0]],
                                    keywords=[]
                                )
                                node.body[idx] = ast.Expr(value=append_call)
                return self.generic_visit(node)

        return LoopOptimizer().visit(new_tree)

    def generate_optimized_code(self) -> str:
        """生成优化后的代码"""
        # 1. 先优化未使用变量
        optimized_tree = self.optimize_unused_variables(self.driver.ast_tree)
        # 2. 再优化低效循环
        optimized_tree = self.optimize_loops(optimized_tree)
        # 3. 将AST转回代码字符串
        self.optimized_code = ast.unparse(optimized_tree)
        return self.optimized_code

# ------------------------------
# 测试用例（可直接运行）
# ------------------------------
if __name__ == "__main__":
    # 待优化的测试代码
    test_code = """
# 存在未使用变量和低效循环
unused_var = 100
result = []
for i in range(10):
    result = result + [i * 2]  # 低效的列表拼接
print(result)
    """
    
    # 1. 初始化静态分析驱动
    analyzer = StaticAnalysisDriver(test_code)
    # 2. 运行静态分析
    analysis_results = analyzer.run_full_analysis()
    print("=== 静态分析结果 ===")
    for issue_type, issues in analysis_results.items():
        if issues:
            print(f"\n{issue_type.upper()}:")
            for line, desc in issues:
                print(f"  - 行{line}: {desc}")
    
    # 3. 初始化优化器并生成优化代码
    optimizer = CodeOptimizer(analyzer)
    optimized_code = optimizer.generate_optimized_code()
    print("\n=== 优化后的代码 ===")
    print(optimized_code)