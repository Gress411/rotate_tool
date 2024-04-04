import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from functools import partial
import os
import subprocess
import threading


def rotate_video(input_path, output_path, angle, progress_var):
    # 打开视频文件
    cap = cv2.VideoCapture(input_path)

    # 获取编解码器
    fourcc = 'mp4v'

    # 获取视频详情
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if angle in [90, 270]:
        frame_width, frame_height = frame_height, frame_width

    # 创建 VideoWriter 对象
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*fourcc), fps, (frame_width, frame_height))

    # 读取视频直到完成
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    current_frame = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            if angle == 90:
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            elif angle == 180:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            elif angle == 270:
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # 写入旋转后的帧
            out.write(frame)

            # 更新进度
            current_frame += 1
            progress_value = int((current_frame / total_frames) * 100)
            progress_var.set(progress_value)
        else:
            break

    # 完成后释放资源
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def browse_file(text_widget):
    filename = filedialog.askopenfilename()
    text_widget.delete(0, tk.END)
    text_widget.insert(0, filename)


def start_rotation(input_path_entry, angle_var, progress_var):
    input_path = input_path_entry.get()
    if not input_path:
        messagebox.showerror("有问题啊", "你这导的是视频吗？")
        return

    angle = angle_var.get()
    output_path = os.path.splitext(input_path)[0] + f"_转{angle}度.mp4"

    # 在单独的线程中旋转视频
    rotate_thread = threading.Thread(target=rotate_video, args=(input_path, output_path, angle, progress_var))
    rotate_thread.start()

    # 在单独的线程中使用 FFmpeg 编码 MP4
    encode_thread = threading.Thread(target=encode_video, args=(output_path,))
    encode_thread.start()


def encode_video(output_path):
    subprocess.call(
        ['ffmpeg', '-i', output_path, '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-c:a', 'aac', '-b:a',
         '128k', '-strict', 'experimental', '-movflags', '+faststart', os.path.splitext(output_path)[0] + "_h264.mp4"])

    # subprocess.
    # messagebox.showinfo("成功", "视频旋转已完成，并以 H.264 MP4 格式导出。")


def main():
    root = tk.Tk()
    root.title("视频旋转")

    input_label = tk.Label(root, text="输入视频路径:")
    input_label.grid(row=0, column=0, sticky="w")

    input_path_entry = tk.Entry(root, width=50)
    input_path_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

    browse_button = tk.Button(root, text="浏览", command=partial(browse_file, input_path_entry))
    browse_button.grid(row=0, column=3, padx=5, pady=5)

    angle_label = tk.Label(root, text="选择旋转角度:")
    angle_label.grid(row=1, column=0, sticky="w")

    angle_var = tk.IntVar(root)
    angle_var.set(90)

    angle_menu = tk.OptionMenu(root, angle_var, 90, 180, 270)
    angle_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

    progress_label = tk.Label(root, text="非常精确的进度条:")
    progress_label.grid(row=2, column=0, sticky="w")

    progress_var = tk.IntVar(root)
    progress_var.set(0)

    progress_bar = ttk.Progressbar(root, mode="determinate", variable=progress_var, length=400)
    progress_bar.grid(row=2, column=1, columnspan=2, pady=5)

    start_button = tk.Button(root, text="开转",
                             command=partial(start_rotation, input_path_entry, angle_var, progress_var))
    start_button.grid(row=3, column=1, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
