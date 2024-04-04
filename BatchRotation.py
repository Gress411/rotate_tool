import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
from concurrent.futures import ThreadPoolExecutor

MAX_THREADS = 4  # 设置同时处理上限，不然卡死你
thread_pool = ThreadPoolExecutor(max_workers=MAX_THREADS)


def rotate_and_encode_video(input_path, output_path, vf_filter, angle):
    command = [
        'ffmpeg', '-i', input_path,
        '-vf', vf_filter,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-c:a', 'aac', '-b:a', ' 128k', '-y',
        '-strict', 'experimental', '-movflags', '+faststart',
        output_path
    ]

    subprocess.call(command)
    # messagebox.showinfo("好！", f"导到这了：{output_path}")


def browse_file(text_widget):
    filename = filedialog.askopenfilename()
    text_widget.delete(0, tk.END)
    text_widget.insert(0, filename)


def start_rotation(input_path_entry, angle_var):
    input_path = input_path_entry.get()
    if not input_path:
        messagebox.showerror("有问题啊", "你这导的是视频吗？")
        return

    angle = angle_var.get()
    output_angle = angle
    vf_filter = ""
    if angle == 90:
        vf_filter = "transpose=1"
        output_angle = 1
    elif angle == 180:
        vf_filter = "transpose=2,transpose=2"
        output_angle = 2
    elif angle == -90:
        vf_filter = "transpose=2"
        output_angle = 3

    output_folder = os.path.join(os.path.dirname(input_path), f"转了{angle}度")
    os.makedirs(output_folder, exist_ok=True)

    input_files = [f for f in os.listdir(os.path.dirname(input_path)) if
                   os.path.isfile(os.path.join(os.path.dirname(input_path), f))]

    for file in input_files:
        input_file_path = os.path.join(os.path.dirname(input_path), file)
        if input_file_path.endswith('.mp4') or input_file_path.endswith('.MP4') or input_file_path.endswith(
                '.avi') or input_file_path.endswith('.AVI') or input_file_path.endswith(
                '.mov') or input_file_path.endswith('.MOV'):
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(file)[0]}_转了{angle}度.mp4")
            # 使用线程池提交任务
            thread_pool.submit(rotate_and_encode_video, input_file_path, output_file_path, vf_filter, output_angle)


def main():
    root = tk.Tk()
    root.title("转视频")

    input_label = tk.Label(root, text="视频路径:")
    input_label.grid(row=0, column=0, sticky="w")

    input_path_entry = tk.Entry(root, width=50)
    input_path_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

    browse_button = tk.Button(root, text="浏览", command=lambda: browse_file(input_path_entry))
    browse_button.grid(row=0, column=3, padx=5, pady=5)

    angle_label = tk.Label(root, text="选择旋转角度:")
    angle_label.grid(row=1, column=0, sticky="w")

    angle_var = tk.IntVar(root)
    angle_var.set(90)  # 初始值为90度

    angle_menu = tk.OptionMenu(root, angle_var, 90, -90, 180)  # 角度菜单，90度、-90度、180度
    angle_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

    start_button = tk.Button(root, text="开转！", command=lambda: start_rotation(input_path_entry, angle_var))
    start_button.grid(row=2, column=1, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
