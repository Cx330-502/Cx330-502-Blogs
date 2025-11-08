import os
import shutil
import re
import pathspec

# --- 配置区 ---
# 1. 设置你的旧 Hexo 博客中 post_pics 文件夹的路径 (相对于脚本运行位置)
#    通常，如果脚本放在项目根目录，这个路径就是正确的。
hexo_pics_root = os.path.join('source', 'files_', 'pics', 'post_pics')
# --- 配置区结束 ---

# 获取当前脚本所在的路径，即项目根目录
project_root = os.getcwd()
posts_root = os.path.join(project_root, 'source', '_posts')
print(f"博客项目根目录: {project_root}")
print(f"文章目录: {posts_root}")
print(f"Hexo 图片源目录: {os.path.join(project_root, hexo_pics_root)}\n")

def find_and_process_files():
    if not os.path.exists(posts_root):
        print(f"[错误] 文章目录 '{posts_root}' 不存在。请确保脚本在正确的项目根目录下运行。")
        return

    for root, dirs, files in os.walk(posts_root):
        for file in files:
            if file.endswith('.md'):
                process_markdown_file(os.path.join(root, file))

def process_markdown_file(md_path):
    md_filename_without_ext = os.path.splitext(os.path.basename(md_path))[0]
    md_dir = os.path.dirname(md_path)

    print(f"--- 正在处理: {md_filename_without_ext}.md ---")

    # 步骤 1: 迁移图片文件夹
    move_images(md_filename_without_ext, md_dir)

    # 步骤 2: 读取文件内容
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            original_content = content
    except Exception as e:
        print(f"    [!] 读取文件失败: {md_path}. 错误: {e}")
        return

    # 步骤 3: 修复图片链接 (正文和 Frontmatter)
    content = fix_image_links(content, md_filename_without_ext)

    # 步骤 4: 修复 Mermaid 语法
    content = fix_mermaid_syntax(content)

    # 步骤 5: 如果有改动，则写回文件
    if content != original_content:
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("    -> 文件内容已成功更新。")
        except Exception as e:
            print(f"    [!] 写入文件失败: {md_path}. 错误: {e}")

def move_images(md_filename, md_dir):
    source_image_folder = None
    # 在旧的图片根目录中查找匹配的文章名文件夹
    for year_month_folder in os.listdir(hexo_pics_root):
        year_month_path = os.path.join(hexo_pics_root, year_month_folder)
        if os.path.isdir(year_month_path):
            for post_folder in os.listdir(year_month_path):
                if post_folder == md_filename:
                    source_image_folder = os.path.join(year_month_path, post_folder)
                    break
        if source_image_folder:
            break

    if not source_image_folder or not os.path.exists(source_image_folder):
        return # 没有找到对应的图片文件夹，正常跳过

    print(f"    [+] 找到匹配的图片文件夹: {source_image_folder}")
    
    # 构建新的目标路径：<md所在目录>/assets/<md文件名>/
    target_image_folder = os.path.join(md_dir, 'assets', md_filename)
    
    # 确保目标路径的父目录(assets)存在
    os.makedirs(os.path.dirname(target_image_folder), exist_ok=True)

    if not os.path.exists(target_image_folder):
        shutil.move(source_image_folder, target_image_folder)
        print(f"    -> 已移动到: {target_image_folder}")
    else:
        print(f"    -> 目标文件夹已存在，将合并文件到: {target_image_folder}")
        for item in os.listdir(source_image_folder):
            shutil.move(os.path.join(source_image_folder, item), os.path.join(target_image_folder, item))
        if not os.listdir(source_image_folder):
            try:
                os.rmdir(source_image_folder)
            except OSError:
                pass # ignore if not empty

def fix_image_links(content, md_filename):
    """根据新的 `assets/<md文件名>` 结构修复链接"""
    # 正则表达式，匹配各种可能的图片路径，只捕获最后的图片文件名
    pattern = r"\(.*?/([^/)]+\.(?:png|jpg|jpeg|gif|svg))\)"
    
    # 新的路径格式
    new_path_format = f"(assets/{md_filename}/\\1)"
    new_content, count = re.subn(pattern, new_path_format, content)
    
    if count > 0:
        print(f"    -> 修复了 {count} 个正文中的图片链接。")
    
    # 单独处理 Frontmatter 中的 'cover:' 字段
    cover_pattern = re.compile(r"^(cover:\s*.*?/)([^/)]+\.(?:png|jpg|jpeg|gif|svg))", re.MULTILINE)
    
    # 新的 cover 路径格式
    new_cover_path_format = fr"\1assets/{md_filename}/\2"
    # 这里我们用一个更简单的替换，直接找到cover行并替换
    def replace_cover(match):
        image_name = match.group(2)
        return f"cover: assets/{md_filename}/{image_name}"

    new_content, count_cover = re.subn(cover_pattern, replace_cover, new_content)

    if count_cover > 0:
         print(f"    -> 修复了 {count_cover} 个 Frontmatter 中的封面链接。")

    return new_content

def fix_mermaid_syntax(content):
    """将 Hexo Mermaid 标签转换为标准 Markdown 代码块"""
    new_content = content.replace('{% mermaid %}', '```mermaid')
    new_content = new_content.replace('{% endmermaid %}', '```')
    
    if new_content != content:
        print("    -> 已将 Hexo Mermaid 语法转换为标准 Markdown。")
        
    return new_content

if __name__ == '__main__':
    if not os.path.exists(hexo_pics_root):
        print(f"[严重错误] 旧图片根目录 '{hexo_pics_root}' 不存在。请检查脚本中的 `hexo_pics_root` 配置是否正确。")
    else:
        find_and_process_files()
        print("\n✅ 迁移完成！您的文件和图片已按 `assets/<文章名>` 结构重新组织。")
        print("请打开 Obsidian 或您的编辑器检查效果。")