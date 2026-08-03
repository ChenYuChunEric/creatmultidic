"""
main.py - 批次資料夾建立工具的 CLI 互動式介面
"""

import sys
from datetime import datetime
from typing import List, Dict, Any
from folder_creator import FolderCreator


def print_divider(char: str = "=", length: int = 60) -> None:
    """列印分隔線。"""
    print(char * length)


def print_results_summary(results: List[Dict[str, Any]]) -> None:
    """
    印出資料夾建立結果統計與詳細明細。

    :param results: 包含建立結果的字典列表
    """
    if not results:
        print("⚠️ 未建立任何資料夾。")
        return

    created_count = sum(1 for r in results if r["status"] == "created")
    exists_count = sum(1 for r in results if r["status"] == "exists")
    error_count = sum(1 for r in results if r["status"] == "error")

    print("\n------------------- 執行結果統計 -------------------")
    print(f"📊 總計處理: {len(results)} 項 | 🟢 建立成功: {created_count} | 🟡 已存在: {exists_count} | 🔴 失敗: {error_count}")
    print("----------------------------------------------------")

    for r in results:
        status_icon = "🟢" if r["status"] == "created" else ("🟡" if r["status"] == "exists" else "🔴")
        print(f" {status_icon} [{r['status'].upper()}] {r['name']} -> {r['message']}")
    print("----------------------------------------------------\n")


def get_integer_input(prompt: str, default: int, min_val: int = 1) -> int:
    """
    取得整數輸入的輔助函式，支援預設值與範圍驗證。

    :param prompt: 提示訊息
    :param default: 預設整數值
    :param min_val: 最小允許值
    :return: 使用者輸入或預設整數
    """
    while True:
        user_input = input(f"{prompt} [預設: {default}]: ").strip()
        if not user_input:
            return default
        try:
            val = int(user_input)
            if val < min_val:
                print(f"⚠️ 輸入數值不能小於 {min_val}，請重新輸入。")
                continue
            return val
        except ValueError:
            print("⚠️ 請輸入有效的整數！")


def handle_custom_names(creator: FolderCreator) -> None:
    """處理自訂名稱批次建立。"""
    print("\n--- 功能 2: 自訂名稱批次建立 ---")
    print("請輸入要建立的資料夾名稱，多個名稱請用「逗號(,)」或「半形空白」分隔。")
    print("範例: 專案A, 專案B, 專案C")
    raw_input = input("👉 輸入名稱: ").strip()

    if not raw_input:
        print("⚠️ 輸入內容為空，取消操作。")
        return

    # 處理逗號或空白分隔
    if "," in raw_input or "，" in raw_input:
        names = [n.strip() for n in raw_input.replace("，", ",").split(",") if n.strip()]
    else:
        names = [n.strip() for n in raw_input.split() if n.strip()]

    if not names:
        print("⚠️ 未解析到有效名稱，取消操作。")
        return

    print(f"\n正在於 [{creator.target_path}] 建立 {len(names)} 個資料夾...")
    results = creator.create_custom_folders(names)
    print_results_summary(results)


def handle_sequential_names(creator: FolderCreator) -> None:
    """處理流水號組合命名。"""
    print("\n--- 功能 3: 流水號組合命名 ---")
    base_name = input("👉 請輸入特定名稱 (留空則僅使用流水號，例如 '專案'): ").strip()
    start_num = get_integer_input("👉 請輸入起始號碼", default=1, min_val=0)
    count = get_integer_input("👉 請輸入建立數量", default=5, min_val=1)
    digits = get_integer_input("👉 請輸入補零位數 (例如 2 代表 01, 3 代表 001)", default=2, min_val=1)

    print("\n請選擇命名順序：")
    print(" 1. 流水號在前 (例如: 01_專案)")
    print(" 2. 特定名稱在前 (例如: 專案_01)")
    order_choice = input("👉 請選擇 (1 或 2) [預設: 1]: ").strip()
    number_first = False if order_choice == "2" else True

    sep = input("👉 請輸入分隔符號 [預設: '_']: ").strip()
    if not sep:
        sep = "_"

    print(f"\n正在於 [{creator.target_path}] 建立 {count} 個流水號資料夾...")
    results = creator.create_sequential_folders(
        base_name=base_name,
        start_num=start_num,
        count=count,
        digits=digits,
        number_first=number_first,
        sep=sep
    )
    print_results_summary(results)


def handle_weekly_names(creator: FolderCreator) -> None:
    """處理週次與日期區間命名。"""
    print("\n--- 功能 4: 週次與日期區間命名 ---")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    while True:
        date_input = input(f"👉 請輸入起始日期 (YYYY-MM-DD) [預設: {today_str}]: ").strip()
        if not date_input:
            start_date_str = today_str
            break
        else:
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                start_date_str = date_input
                break
            except ValueError:
                print("⚠️ 日期格式不正確！請使用 YYYY-MM-DD 格式 (例如: 2026-08-03)。")

    total_weeks = get_integer_input("👉 請輸入總週數", default=4, min_val=1)

    print("\n請選擇週次格式：")
    print(" 1. 國字數字 (例如: 1.第一周(0803-0809))")
    print(" 2. 阿拉伯數字 (例如: 1.第1周(0803-0809))")
    fmt_choice = input("👉 請選擇 (1 或 2) [預設: 1]: ").strip()
    use_chinese = False if fmt_choice == "2" else True

    print(f"\n正在於 [{creator.target_path}] 建立 {total_weeks} 週的週次資料夾...")
    try:
        results = creator.create_weekly_folders(start_date_str, total_weeks, use_chinese_number=use_chinese)
        print_results_summary(results)
    except ValueError as ve:
        print(f"🔴 建立失敗: {ve}")


def main() -> None:
    """CLI 主程式進入點。"""
    creator = FolderCreator(target_path="./")

    while True:
        print_divider("=")
        print("        📂 批次資料夾建立工具 (Batch Folder Creator)")
        print_divider("=")
        print(f"📍 當前目標資料夾路徑: {creator.target_path}")
        print_divider("-")
        print(" 1. 設定 / 變更目標資料夾路徑")
        print(" 2. 自訂名稱批次建立")
        print(" 3. 流水號組合命名建立 (如: 01_專案 或 專案_01)")
        print(" 4. 週次與日期區間命名建立 (如: 1.第一周(0803-0809))")
        print(" 0. 離開程式")
        print_divider("=")

        choice = input("👉 請選擇功能編號 (0-4): ").strip()

        if choice == "1":
            print("\n--- 功能 1: 設定 / 變更目標資料夾路徑 ---")
            new_path = input("👉 請輸入目標資料夾路徑 (留空則重置為當前目錄 './'): ").strip()
            creator.set_target_path(new_path)
            success, msg = creator.ensure_target_path_exists()
            if success:
                print(f"✅ {msg}\n")
            else:
                print(f"⚠️ {msg}\n")

        elif choice == "2":
            handle_custom_names(creator)

        elif choice == "3":
            handle_sequential_names(creator)

        elif choice == "4":
            handle_weekly_names(creator)

        elif choice == "0":
            print("\n感謝使用批次資料夾建立工具，再見！👋")
            sys.exit(0)

        else:
            print("\n⚠️ 無效的選項，請重新輸入 (0-4)！\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程式已由使用者中斷。再見！👋")
        sys.exit(0)
