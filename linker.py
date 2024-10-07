
"""
developer: Ookami
vision: 0.0.4
新增和github文件同步功能

"""
import os
import requests
from bs4 import BeautifulSoup
import random
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import textwrap

# GitHub 仓库页面 URL 和信息
repository_url = "https://github.com/saookami/hihi"
username = "saookami"
repository = "hihi"
branch = "main"  # 通常是 'main' 或 'master'
local_data_dir = "hihi"  # 存储图片和文本文件的本地文件夹

# 确保本地文件夹存在
if not os.path.exists(local_data_dir):
    os.makedirs(local_data_dir)


# 获取 GitHub 仓库页面的 HTML 内容
def get_github_files(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except (requests.RequestException, ValueError):
        print("无法连接到 GitHub，使用本地缓存文件")
        return None


# 提取页面中所有文件名，并生成对应的 Raw URL
def extract_files_from_html(html_content):
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    file_links = []

    for link in soup.find_all('a', class_='Link--primary'):
        href = link.get('href')
        if href and href.startswith(f'/{username}/{repository}/blob/{branch}/'):
            raw_url = href.replace('/blob/', '/')
            raw_url = f"https://raw.githubusercontent.com{raw_url}"
            file_links.append(raw_url)
    return file_links


# 从远程下载文件并保存到本地
def download_and_save_file(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, 'wb') as file:
            file.write(response.content)
    except (requests.RequestException, ValueError):
        print(f"下载失败：{url}")


# 删除本地多余的文件
def remove_obsolete_files(github_files):
    # 获取 GitHub 文件的文件名（不包含路径）
    github_file_names = [os.path.basename(url) for url in github_files]

    # 遍历本地文件夹，删除不存在于 GitHub 上的文件
    for local_file in os.listdir(local_data_dir):
        if local_file not in github_file_names:
            local_file_path = os.path.join(local_data_dir, local_file)
            print(f"删除本地文件：{local_file_path}")
            os.remove(local_file_path)


# 检查并下载更新的文件到本地
def update_local_files(file_links):
    for file_url in file_links:
        file_name = file_url.split("/")[-1]
        local_path = os.path.join(local_data_dir, file_name)

        # 如果本地没有该文件或者文件过旧，则下载更新
        if not os.path.exists(local_path):
            print(f"下载新文件：{file_name}")
            download_and_save_file(file_url, local_path)


# 从本地文件夹中读取文件名
def get_local_files():
    local_files = [os.path.join(local_data_dir, file) for file in os.listdir(local_data_dir)]
    image_files = [file for file in local_files if file.endswith(('.png', '.jpg', '.jpeg'))]
    text_files = [file for file in local_files if file.endswith('.txt')]
    return image_files, text_files


# 随机选择一个图片和一个文本
def select_random_files():
    image_files, text_files = get_local_files()
    if not image_files or not text_files:
        raise ValueError("No image or text files found locally. Please check the data folder.")
    selected_image = random.choice(image_files)
    selected_text = random.choice(text_files)
    return selected_image, selected_text


# 从本地获取图片，并保持长宽比
def fetch_image(image_path, max_width=400, max_height=300):
    image = Image.open(image_path)
    original_width, original_height = image.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)  # 调整图片大小，并保持长宽比
    return image


# 从本地获取文本
def fetch_text(text_path):
    with open(text_path, 'r', encoding='utf-8') as file:
        return file.read().strip()


# 将长文本分成多行
def wrap_text(text, max_width=20):
    wrapped_text = "\n".join(textwrap.wrap(text, width=max_width))  # 将文本按指定宽度换行
    return wrapped_text


# 更新内容并在 Tkinter 窗口中显示
def update_content(image_path, text_path):
    # 获取图片和文字
    image = fetch_image(image_path)
    text = fetch_text(text_path)
    text = wrap_text(text, max_width=40)  # 将文本自动分行

    # 将图像转换为 Tkinter 格式
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo  # 防止被垃圾回收

    # 设置动态文字显示的初始状态
    text_index = 0  # 文字当前显示的索引
    delay = 100  # 每个字符显示的时间间隔（毫秒）

    def animate_text():
        nonlocal text_index
        current_text = text[:text_index]  # 动态显示部分文字
        text_label.config(text=current_text)  # 更新显示的文字内容
        text_label.update()  # 刷新显示的 Label

        # 更新下一个字符
        if text_index < len(text):
            text_index += 1
            root.after(delay, animate_text)  # 设置定时器，实现动态效果

    animate_text()  # 启动文字动画


# 获取 GitHub 仓库中的所有文件链接
html_content = get_github_files(repository_url)
file_links = extract_files_from_html(html_content)

# 如果能够连接到 GitHub，检查更新并删除本地过时文件
if file_links:
    update_local_files(file_links)  # 下载新的文件
    remove_obsolete_files(file_links)  # 删除已经被 GitHub 删除的文件

# 随机选择图片和文本文件
selected_image, selected_text = select_random_files()

# 创建 Tkinter 窗口
root = tk.Tk()
root.title("Surprise Message")

# 设置窗口大小和位置
window_width, window_height = 500, 600  # 设置窗口大小以容纳图片和文字区域
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_right = int(screen_width / 2 - window_width / 2)
position_down = int(screen_height / 2 - window_height / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

# 创建并布局显示图片和文字的 Label
image_label = Label(root)  # 用于显示图片的 Label
image_label.pack(pady=10)  # 添加一些间距

text_label = Label(root, text="", font=("Arial", 16), wraplength=window_width - 20, justify="left")  # 用于显示文字的 Label
text_label.pack(pady=10)  # 文字区域与图片区域之间添加间距

# 获取本地内容并更新界面
update_content(selected_image, selected_text)

# 运行 Tkinter 主循环
root.mainloop()
