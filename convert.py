import os
import re

# --- 配置 ---
# 文章所在的目录
posts_dir = os.path.join('source', '_posts')
# --- 结束 ---

def process_all_markdown_files():
    """
    遍历所有文章，移除图片链接中多余的 'assets/<文章名>/' 前缀。
    """
    print("Starting link conversion for Hexo deployment...")
    if not os.path.isdir(posts_dir):
        print(f"Error: Posts directory '{posts_dir}' not found.")
        return

    for root, _, files in os.walk(posts_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                md_filename_without_ext = os.path.splitext(file)[0]
                
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        original_content = content
                    
                    # 1. 修复正文中的链接：(assets/文章名/图片.png) -> (图片.png)
                    # 使用 re.escape 来安全处理文件名中的特殊字符
                    body_pattern = re.compile(r"\(assets/" + re.escape(md_filename_without_ext) + r"/([^/)]+)\)")
                    content = body_pattern.sub(r"(\1)", content)
                    
                    # 2. 修复 Frontmatter 中的 cover 链接
                    cover_pattern = re.compile(r"^(cover:\s*)assets/" + re.escape(md_filename_without_ext) + r"/([^/)]+)", re.MULTILINE)
                    content = cover_pattern.sub(r"\1\2", content)
                    
                    if content != original_content:
                        with open(md_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"  - Converted links in: {file}")

                except Exception as e:
                    print(f"  - Error processing {file}: {e}")
    
    print("Link conversion complete.")

if __name__ == '__main__':
    process_all_markdown_files()