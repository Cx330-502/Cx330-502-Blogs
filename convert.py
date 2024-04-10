import os


def convert_markdown_mermaid_code_to_hexo_mermaid_code(file_path, repo0):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    flag = False
    for i in range(0, len(content)):
        if i + 10 < len(content) and content[i] == '`' and content[i + 1] == '`' and content[i + 2] == '`' and \
                content[i + 3] == 'm' and content[i + 4] == 'e' and content[i + 5] == 'r' and \
                content[i + 6] == 'm' and content[i + 7] == 'a' and content[i + 8] == 'i' and \
                content[i + 9] == 'd' and content[i + 10] == '\n' and not flag:
            content = content[:i] + '{% mermaid %}' + content[i + 10:]
            flag = True
        if i + 2 < len(content) and content[i] == '`' and content[i + 1] == '`' and content[i + 2] == '`' and flag:
            content = content[:i] + '{% endmermaid %}' + content[i + 3:]
            flag = False
    content = content.replace('(./../../files_/pics/', '(/' + repo0 + '/files_/pics/')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == '__main__':
    repo = 'Cx330-502-Blogs'
    for root, dirs, files in os.walk('./source/_posts'):
        for file in files:
            if file.endswith('.md'):
                print("Converting file: " + file)
                convert_markdown_mermaid_code_to_hexo_mermaid_code(os.path.join(root, file), repo)
