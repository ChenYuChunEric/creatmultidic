"""
gui.py - 批次資料夾建立工具的 GUI 圖形介面
"""

import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from folder_creator import FolderCreator


class FolderCreatorGUI(tk.Tk):
    """批次資料夾建立工具 GUI 主視窗類別"""

    def __init__(self) -> None:
        super().__init__()

        self.title("📂 批次資料夾建立工具 (Batch Folder Creator)")
        self.geometry("680x560")
        self.minsize(600, 480)

        # 核心邏輯物件
        self.creator = FolderCreator(target_path="./")

        # 設定風格主題
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("vista")  # Windows 上質感較佳的主題
        except Exception:
            pass

        self._create_widgets()
        self._init_default_values()

    def _create_widgets(self) -> None:
        """建立 UI 元件與佈局"""
        # ==========================================
        # 1. 頂部: 目標路徑選擇區
        # ==========================================
        path_frame = ttk.LabelFrame(self, text=" 📍 目標路徑設定 ", padding=10)
        path_frame.pack(fill=tk.X, padx=12, pady=8)

        ttk.Label(path_frame, text="目標資料夾:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.path_var = tk.StringVar(value=self.creator.target_path)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        browse_btn = ttk.Button(path_frame, text="📁 瀏覽...", command=self._browse_target_path)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # ==========================================
        # 2. 中間: 功能分頁區 (Notebook)
        # ==========================================
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=False, padx=12, pady=5)

        # 頁籤 1: 自訂名稱
        self.tab_custom = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_custom, text=" 📝 自訂名稱批次建立 ")
        self._build_tab_custom()

        # 頁籤 2: 流水號命名
        self.tab_seq = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_seq, text=" 🔢 流水號組合命名 ")
        self._build_tab_sequential()

        # 頁籤 3: 週次與日期
        self.tab_week = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_week, text=" 📅 週次與日期區間 ")
        self._build_tab_weekly()

        # ==========================================
        # 3. 底部: 日誌與訊息顯示區
        # ==========================================
        log_frame = ttk.LabelFrame(self, text=" 📋 執行紀錄與狀態顯示 ", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(5, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED, wrap=tk.WORD, font=("Segoe UI", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 日誌顏色 Tag
        self.log_text.tag_config("CREATED", foreground="#107C41", font=("Segoe UI", 9, "bold"))  # 綠色
        self.log_text.tag_config("EXISTS", foreground="#D83B01", font=("Segoe UI", 9))          # 橘紅色
        self.log_text.tag_config("ERROR", foreground="#A80000", font=("Segoe UI", 9, "bold"))   # 深紅色
        self.log_text.tag_config("INFO", foreground="#002050")                                  # 深藍色

    def _build_tab_custom(self) -> None:
        """建立頁籤 1: 自訂名稱 UI"""
        ttk.Label(self.tab_custom, text="請輸入要建立的資料夾名稱（多個名稱請用「逗號(,)」或「換行」分隔）:").pack(anchor=tk.W, pady=(0, 5))
        
        self.custom_names_text = scrolledtext.ScrolledText(self.tab_custom, height=4, wrap=tk.WORD)
        self.custom_names_text.pack(fill=tk.X, pady=(0, 10))
        self.custom_names_text.insert(tk.END, "專案A, 專案B, 專案C")

        btn_run = ttk.Button(self.tab_custom, text="🚀 開始建立自訂資料夾", command=self._run_custom_creation)
        btn_run.pack(anchor=tk.E)

    def _build_tab_sequential(self) -> None:
        """建立頁籤 2: 流水號組合命名 UI"""
        grid_frame = ttk.Frame(self.tab_seq)
        grid_frame.pack(fill=tk.X, pady=5)

        # 特定名稱
        ttk.Label(grid_frame, text="特定名稱:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.seq_basename_var = tk.StringVar(value="專案")
        ttk.Entry(grid_frame, textvariable=self.seq_basename_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)

        # 起始號碼
        ttk.Label(grid_frame, text="起始號碼:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=4)
        self.seq_start_var = tk.IntVar(value=1)
        ttk.Spinbox(grid_frame, from_=0, to=9999, textvariable=self.seq_start_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5, pady=4)

        # 建立數量
        ttk.Label(grid_frame, text="建立數量:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=4)
        self.seq_count_var = tk.IntVar(value=5)
        ttk.Spinbox(grid_frame, from_=1, to=1000, textvariable=self.seq_count_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)

        # 補零位數
        ttk.Label(grid_frame, text="補零位數:").grid(row=1, column=2, sticky=tk.W, padx=(20, 5), pady=4)
        self.seq_digits_var = tk.IntVar(value=2)
        ttk.Spinbox(grid_frame, from_=1, to=10, textvariable=self.seq_digits_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=4)

        # 命名順序
        ttk.Label(grid_frame, text="命名順序:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=4)
        self.seq_order_var = tk.StringVar(value="num_first")
        order_frame = ttk.Frame(grid_frame)
        order_frame.grid(row=2, column=1, columnspan=3, sticky=tk.W, padx=5, pady=4)
        
        ttk.Radiobutton(order_frame, text="流水號在前 (例如 01_專案)", variable=self.seq_order_var, value="num_first").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(order_frame, text="名稱在前 (例如 專案_01)", variable=self.seq_order_var, value="name_first").pack(side=tk.LEFT)

        # 分隔符號
        ttk.Label(grid_frame, text="分隔符號:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=4)
        self.seq_sep_var = tk.StringVar(value="_")
        ttk.Entry(grid_frame, textvariable=self.seq_sep_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=4)

        btn_run = ttk.Button(self.tab_seq, text="🚀 開始建立流水號資料夾", command=self._run_sequential_creation)
        btn_run.pack(anchor=tk.E, pady=(10, 0))

    def _build_tab_weekly(self) -> None:
        """建立頁籤 3: 週次與日期區間 UI"""
        grid_frame = ttk.Frame(self.tab_week)
        grid_frame.pack(fill=tk.X, pady=5)

        # 起始日期
        ttk.Label(grid_frame, text="起始日期 (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.week_start_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(grid_frame, textvariable=self.week_start_date_var, width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=8)

        # 總週數
        ttk.Label(grid_frame, text="總週數:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.week_total_var = tk.IntVar(value=4)
        ttk.Spinbox(grid_frame, from_=1, to=100, textvariable=self.week_total_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=8)

        # 週次標示格式 (國字 vs 阿拉伯數字)
        ttk.Label(grid_frame, text="週次格式:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=8)
        self.week_num_type_var = tk.StringVar(value="chinese")
        num_type_frame = ttk.Frame(grid_frame)
        num_type_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=8)
        ttk.Radiobutton(num_type_frame, text="國字 (例: 第一周)", variable=self.week_num_type_var, value="chinese").pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(num_type_frame, text="阿拉伯數字 (例: 第1周)", variable=self.week_num_type_var, value="arabic").pack(side=tk.LEFT)

        ttk.Label(self.tab_week, text="💡 產生格式範例: 1.第一周(0803-0809) 或 1.第1周(0803-0809)", font=("Segoe UI", 9, "italic")).pack(anchor=tk.W, pady=5)

        btn_run = ttk.Button(self.tab_week, text="🚀 開始建立週次資料夾", command=self._run_weekly_creation)
        btn_run.pack(anchor=tk.E, pady=(10, 0))

    def _init_default_values(self) -> None:
        """初始更新日誌訊息"""
        self._append_log("系統就緒！請先選擇目標路徑或直接開始建立。", "INFO")

    def _browse_target_path(self) -> None:
        """點擊瀏覽按鈕，開起選擇資料夾視窗"""
        current_path = self.path_var.get().strip() or "./"
        selected = filedialog.askdirectory(initialdir=current_path, title="選擇目標資料夾")
        if selected:
            self.path_var.set(selected)
            self.creator.set_target_path(selected)
            self._append_log(f"目標路徑已變更為: {self.creator.target_path}", "INFO")

    def _update_creator_target_path(self) -> bool:
        """同步 Entry 的目標路徑至 FolderCreator"""
        path = self.path_var.get().strip()
        if not path:
            path = "./"
        self.creator.set_target_path(path)
        success, msg = self.creator.ensure_target_path_exists()
        if not success:
            messagebox.showerror("錯誤", f"無法準備目標目錄：\n{msg}")
            self._append_log(msg, "ERROR")
            return False
        return True

    def _append_log(self, text: str, tag: str = "INFO") -> None:
        """向 ScrolledText 寫入日誌"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {text}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_results(self, results: list) -> None:
        """處理並列印建立結果統計"""
        if not results:
            self._append_log("未建立任何資料夾。", "INFO")
            return

        created_count = sum(1 for r in results if r["status"] == "created")
        exists_count = sum(1 for r in results if r["status"] == "exists")
        error_count = sum(1 for r in results if r["status"] == "error")

        self._append_log(
            f"=== 處理完成 | 總數: {len(results)} | 🟢 新增: {created_count} | 🟡 已存在: {exists_count} | 🔴 失敗: {error_count} ===",
            "INFO"
        )

        for r in results:
            if r["status"] == "created":
                self._append_log(f" 🟢 [成功] {r['name']}", "CREATED")
            elif r["status"] == "exists":
                self._append_log(f" 🟡 [已存在] {r['name']}", "EXISTS")
            else:
                self._append_log(f" 🔴 [失敗] {r['name']} - {r['message']}", "ERROR")

    # ==========================================
    # 按鈕觸發事件處理
    # ==========================================
    def _run_custom_creation(self) -> None:
        if not self._update_creator_target_path():
            return

        raw_content = self.custom_names_text.get("1.0", tk.END).strip()
        if not raw_content:
            messagebox.showwarning("提示", "請輸入至少一個資料夾名稱！")
            return

        # 同時支援逗號、頓號與換行切分
        lines = raw_content.replace("，", ",").replace("、", ",").split("\n")
        names = []
        for line in lines:
            for n in line.split(","):
                clean_n = n.strip()
                if clean_n:
                    names.append(clean_n)

        if not names:
            messagebox.showwarning("提示", "未解析到有效的資料夾名稱！")
            return

        self._append_log(f"開始於 [{self.creator.target_path}] 批次建立自訂資料夾 ({len(names)} 個)...", "INFO")
        results = self.creator.create_custom_folders(names)
        self._log_results(results)

    def _run_sequential_creation(self) -> None:
        if not self._update_creator_target_path():
            return

        base_name = self.seq_basename_var.get().strip()
        try:
            start_num = int(self.seq_start_var.get())
            count = int(self.seq_count_var.get())
            digits = int(self.seq_digits_var.get())
        except ValueError:
            messagebox.showerror("錯誤", "數字欄位 (起始號碼、數量、補零位數) 必須為有效的整數！")
            return

        if count <= 0:
            messagebox.showwarning("提示", "建立數量必須大於 0！")
            return

        number_first = (self.seq_order_var.get() == "num_first")
        sep = self.seq_sep_var.get()

        self._append_log(f"開始於 [{self.creator.target_path}] 建立流水號資料夾 ({count} 個)...", "INFO")
        results = self.creator.create_sequential_folders(
            base_name=base_name,
            start_num=start_num,
            count=count,
            digits=digits,
            number_first=number_first,
            sep=sep
        )
        self._log_results(results)

    def _run_weekly_creation(self) -> None:
        if not self._update_creator_target_path():
            return

        date_str = self.week_start_date_var.get().strip()
        try:
            total_weeks = int(self.week_total_var.get())
        except ValueError:
            messagebox.showerror("錯誤", "總週數必須為有效的整數！")
            return

        if total_weeks <= 0:
            messagebox.showwarning("提示", "總週數必須大於 0！")
            return

        use_chinese = (self.week_num_type_var.get() == "chinese")

        self._append_log(f"開始於 [{self.creator.target_path}] 建立週次資料夾 ({total_weeks} 週)...", "INFO")
        try:
            results = self.creator.create_weekly_folders(date_str, total_weeks, use_chinese_number=use_chinese)
            self._log_results(results)
        except ValueError as ve:
            messagebox.showerror("日期格式錯誤", str(ve))
            self._append_log(f"日期格式錯誤: {ve}", "ERROR")


if __name__ == "__main__":
    app = FolderCreatorGUI()
    app.mainloop()
