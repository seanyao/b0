#!/usr/bin/env python3
"""
智能 Git 提交脚本
自动分析代码变更并生成合适的 commit message
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple

class GitCommitHelper:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)
    
    def run_command(self, command: str) -> str:
        """运行命令并返回输出"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {command}")
            print(f"错误: {e.stderr}")
            return ""
    
    def get_git_status(self) -> Dict[str, List[str]]:
        """获取 git 状态"""
        status_output = self.run_command("git status --porcelain")
        changes = {
            'modified': [],
            'added': [],
            'deleted': [],
            'renamed': [],
            'untracked': []
        }
        
        for line in status_output.split('\n'):
            if not line.strip():
                continue
                
            # git status --porcelain 格式: XY PATH
            # X = 暂存区状态, Y = 工作区状态
            # 空格表示无变化
            status = line[:2]
            filename = line[3:]
            
            # 处理各种状态组合
            if 'M' in status:  # 修改
                changes['modified'].append(filename)
            elif 'A' in status:  # 新增
                changes['added'].append(filename)
            elif 'D' in status:  # 删除
                changes['deleted'].append(filename)
            elif 'R' in status:  # 重命名
                changes['renamed'].append(filename)
            elif status == '??':  # 未跟踪
                changes['untracked'].append(filename)
        
        return changes
    
    def analyze_changes(self, changes: Dict[str, List[str]]) -> str:
        """分析变更并生成 commit message"""
        if not any(changes.values()):
            return "无变更需要提交"
        
        # 分析变更类型
        modified_files = changes['modified']
        added_files = changes['added']
        deleted_files = changes['deleted']
        untracked_files = changes['untracked']
        
        # 生成变更描述
        descriptions = []
        
        # 处理修改的文件
        if modified_files:
            modified_categories = self._categorize_files(modified_files)
            for category, files in modified_categories.items():
                if len(files) == 1:
                    descriptions.append(f"更新{category}: {files[0]}")
                else:
                    descriptions.append(f"更新{category}: {len(files)}个文件")
        
        # 处理新增的文件
        if added_files:
            added_categories = self._categorize_files(added_files)
            for category, files in added_categories.items():
                if len(files) == 1:
                    descriptions.append(f"新增{category}: {files[0]}")
                else:
                    descriptions.append(f"新增{category}: {len(files)}个文件")
        
        # 处理删除的文件
        if deleted_files:
            deleted_categories = self._categorize_files(deleted_files)
            for category, files in deleted_categories.items():
                if len(files) == 1:
                    descriptions.append(f"删除{category}: {files[0]}")
                else:
                    descriptions.append(f"删除{category}: {len(files)}个文件")
        
        # 处理未跟踪的文件
        if untracked_files:
            untracked_categories = self._categorize_files(untracked_files)
            for category, files in untracked_categories.items():
                if len(files) == 1:
                    descriptions.append(f"新增{category}: {files[0]}")
                else:
                    descriptions.append(f"新增{category}: {len(files)}个文件")
        
        # 组合成最终的 commit message
        if len(descriptions) == 1:
            return descriptions[0]
        elif len(descriptions) <= 3:
            return " | ".join(descriptions)
        else:
            # 如果描述太多，进行概括
            return self._summarize_changes(changes)
    
    def _categorize_files(self, files: List[str]) -> Dict[str, List[str]]:
        """将文件按类型分类"""
        categories = {
            '文档': [],
            '源代码': [],
            '测试': [],
            '工具': [],
            '配置': [],
            '其他': []
        }
        
        for file in files:
            if file.endswith(('.md', '.txt', '.rst')):
                categories['文档'].append(file)
            elif file.startswith('src/') or file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c')):
                categories['源代码'].append(file)
            elif file.startswith('tests/') or file.endswith('_test.py') or file.startswith('test_'):
                categories['测试'].append(file)
            elif file.startswith('tools/') or file.startswith('tool_'):
                categories['工具'].append(file)
            elif file.endswith(('.yml', '.yaml', '.json', '.toml', '.ini', '.cfg')):
                categories['配置'].append(file)
            else:
                categories['其他'].append(file)
        
        # 移除空分类
        return {k: v for k, v in categories.items() if v}
    
    def _summarize_changes(self, changes: Dict[str, List[str]]) -> str:
        """概括变更"""
        total_changes = sum(len(files) for files in changes.values())
        
        if total_changes <= 5:
            return f"批量更新: {total_changes}个文件"
        else:
            return f"重构和优化: {total_changes}个文件"
    
    def commit_and_push(self, message: str = None):
        """执行提交和推送"""
        # 获取变更状态
        changes = self.get_git_status()
        
        if not any(changes.values()):
            print("没有变更需要提交")
            return
        
        # 生成 commit message
        if not message:
            message = self.analyze_changes(changes)
        
        print(f"变更分析:")
        for change_type, files in changes.items():
            if files:
                print(f"  {change_type}: {len(files)} 个文件")
        
        print(f"\n建议的 commit message: {message}")
        
        # 询问用户是否继续
        user_input = input("\n是否继续提交? (y/N): ").strip().lower()
        if user_input not in ['y', 'yes']:
            print("取消提交")
            return
        
        try:
            # 添加所有变更
            print("添加文件...")
            self.run_command("git add .")
            
            # 提交
            print("提交变更...")
            self.run_command(f'git commit -m "{message}"')
            
            # 推送
            print("推送到远程仓库...")
            self.run_command("git push")
            
            print("✅ 提交成功!")
            
        except Exception as e:
            print(f"❌ 提交失败: {e}")
            return
    
    def show_status(self):
        """显示当前状态"""
        print("当前 Git 状态:")
        print("-" * 50)
        
        changes = self.get_git_status()
        for change_type, files in changes.items():
            if files:
                print(f"\n{change_type.upper()}:")
                for file in files:
                    print(f"  {file}")
        
        if not any(changes.values()):
            print("工作区干净，没有变更")
    
    def interactive_mode(self):
        """交互模式"""
        while True:
            print("\n" + "=" * 50)
            print("Git 提交助手")
            print("=" * 50)
            print("1. 查看状态")
            print("2. 智能提交")
            print("3. 自定义提交")
            print("4. 退出")
            
            choice = input("\n请选择操作 (1-4): ").strip()
            
            if choice == '1':
                self.show_status()
            elif choice == '2':
                self.commit_and_push()
            elif choice == '3':
                message = input("请输入 commit message: ").strip()
                if message:
                    self.commit_and_push(message)
                else:
                    print("commit message 不能为空")
            elif choice == '4':
                print("再见!")
                break
            else:
                print("无效选择，请重试")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        helper = GitCommitHelper()
        
        if sys.argv[1] == 'status':
            helper.show_status()
        elif sys.argv[1] == 'commit':
            message = sys.argv[2] if len(sys.argv) > 2 else None
            helper.commit_and_push(message)
        elif sys.argv[1] == 'interactive':
            helper.interactive_mode()
        else:
            print("用法:")
            print("  python git_commit.py status          # 查看状态")
            print("  python git_commit.py commit [msg]    # 智能提交")
            print("  python git_commit.py interactive     # 交互模式")
    else:
        # 默认交互模式
        helper = GitCommitHelper()
        helper.interactive_mode()

if __name__ == "__main__":
    main()
