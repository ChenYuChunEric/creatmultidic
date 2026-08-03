"""
folder_creator.py - 批次資料夾建立工具的核心邏輯模組

本模組提供 FolderCreator 類別，負責處理：
1. 目標路徑規範與自動建立
2. 自訂名稱批次建立資料夾
3. 流水號組合命名建立資料夾
4. 週次與日期區間命名建立資料夾（含中文數字轉換）
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple


def int_to_chinese_number(num: int) -> str:
    """
    將正整數 (1~999) 轉換為中文數字字串。
    
    範例：
        1 -> "一"
        10 -> "十"
        15 -> "十五"
        20 -> "二十"
        25 -> "二十五"
        100 -> "一百"
        112 -> "一百一十二"

    :param num: 欲轉換的正整數
    :return: 中文數字字串
    """
    if num <= 0 or num >= 1000:
        return str(num)

    digits = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    
    if num < 10:
        return digits[num]
    elif num < 20:
        if num == 10:
            return "十"
        return "十" + digits[num % 10]
    elif num < 100:
        tens = num // 10
        ones = num % 10
        res = digits[tens] + "十"
        if ones != 0:
            res += digits[ones]
        return res
    else:
        hundreds = num // 100
        remainder = num % 100
        res = digits[hundreds] + "百"
        if remainder == 0:
            return res
        elif remainder < 10:
            res += "零" + digits[remainder]
        elif remainder < 20:
            if remainder == 10:
                res += "一十"
            else:
                res += "一十" + digits[remainder % 10]
        else:
            tens = remainder // 10
            ones = remainder % 10
            res += digits[tens] + "十"
            if ones != 0:
                res += digits[ones]
        return res


class FolderCreator:
    """
    批次資料夾建立器類別
    """

    def __init__(self, target_path: str = "./") -> None:
        """
        初始化 FolderCreator。

        :param target_path: 目標輸出的資料夾路徑，預設為當前目錄 ('./')
        """
        self._target_path: str = ""
        self.set_target_path(target_path)

    @property
    def target_path(self) -> str:
        """取得當前設定的目標路徑。"""
        return self._target_path

    def set_target_path(self, target_path: str) -> None:
        """
        設定目標資料夾路徑。

        :param target_path: 目標路徑字串
        """
        if not target_path or not target_path.strip():
            target_path = "./"
        self._target_path = os.path.abspath(target_path.strip())

    def ensure_target_path_exists(self) -> Tuple[bool, str]:
        """
        確保目標父目錄存在，若不存在則自動建立。

        :return: (是否成功/已存在, 訊息說明)
        """
        try:
            os.makedirs(self._target_path, exist_ok=True)
            return True, f"目標目錄準備就緒: {self._target_path}"
        except Exception as e:
            return False, f"建立目標目錄失敗 ({self._target_path}): {str(e)}"

    def _create_single_folder(self, folder_name: str) -> Dict[str, Any]:
        """
        建立單一資料夾的私有輔助方法。

        :param folder_name: 資料夾名稱
        :return: 結果字典 {'name': str, 'path': str, 'status': str, 'message': str}
                 status 可能值: 'created', 'exists', 'error'
        """
        full_path = os.path.join(self._target_path, folder_name)
        result = {
            "name": folder_name,
            "path": full_path,
            "status": "error",
            "message": ""
        }

        try:
            # 先確認目標父路徑存在
            success, msg = self.ensure_target_path_exists()
            if not success:
                result["status"] = "error"
                result["message"] = msg
                return result

            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    result["status"] = "exists"
                    result["message"] = "已存在"
                else:
                    result["status"] = "error"
                    result["message"] = "同名檔案已存在（非資料夾）"
            else:
                os.makedirs(full_path)
                result["status"] = "created"
                result["message"] = "建立成功"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"建立失敗: {str(e)}"

        return result

    def create_custom_folders(self, folder_names: List[str]) -> List[Dict[str, Any]]:
        """
        1. 自訂名稱批次建立資料夾。

        :param folder_names: 資料夾名稱列表
        :return: 建立結果列表
        """
        results = []
        for name in folder_names:
            clean_name = name.strip()
            if not clean_name:
                continue
            res = self._create_single_folder(clean_name)
            results.append(res)
        return results

    def create_sequential_folders(
        self,
        base_name: str,
        start_num: int = 1,
        count: int = 5,
        digits: int = 2,
        number_first: bool = True,
        sep: str = "_"
    ) -> List[Dict[str, Any]]:
        """
        2. 流水號組合命名批次建立資料夾。

        :param base_name: 特定名稱 (如 "專案")
        :param start_num: 起始號碼 (如 1)
        :param count: 建立數量 (如 5)
        :param digits: 補零位數 (如 2 代表 01, 3 代表 001)
        :param number_first: True 表示流水號在前 ("01_專案")，False 表示特定名稱在前 ("專案_01")
        :param sep: 流水號與名稱之間的分隔符號，預設為 "_"
        :return: 建立結果列表
        """
        results = []
        if count <= 0:
            return results
        if digits <= 0:
            digits = 1

        for i in range(count):
            num = start_num + i
            num_str = f"{num:0{digits}d}"
            
            if not base_name.strip():
                folder_name = num_str
            elif number_first:
                folder_name = f"{num_str}{sep}{base_name.strip()}"
            else:
                folder_name = f"{base_name.strip()}{sep}{num_str}"

            res = self._create_single_folder(folder_name)
            results.append(res)

        return results

    def create_weekly_folders(
        self,
        start_date_str: str,
        total_weeks: int,
        use_chinese_number: bool = True
    ) -> List[Dict[str, Any]]:
        """
        3. 週次與日期區間命名批次建立資料夾。
        格式範例： 
          - 中文數字 (use_chinese_number=True): `1.第一周(0803-0809)`
          - 阿拉伯數字 (use_chinese_number=False): `1.第1周(0803-0809)`

        :param start_date_str: 起始日期字串 (格式 YYYY-MM-DD，如 "2026-08-03")
        :param total_weeks: 總週數 (如 4)
        :param use_chinese_number: True 使用國字數字 (第一周)，False 使用阿拉伯數字 (第1周)
        :return: 建立結果列表
        :raises ValueError: 當日期格式不符 YYYY-MM-DD 時拋出
        """
        results = []
        if total_weeks <= 0:
            return results

        try:
            start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("日期格式不正確，請使用 YYYY-MM-DD 格式 (例如: 2026-08-03)")

        for week_idx in range(1, total_weeks + 1):
            week_start = start_date + timedelta(days=(week_idx - 1) * 7)
            week_end = week_start + timedelta(days=6)

            if use_chinese_number:
                week_str = int_to_chinese_number(week_idx)
            else:
                week_str = str(week_idx)

            start_mmdd = week_start.strftime("%m%d")
            end_mmdd = week_end.strftime("%m%d")

            # 格式：1.第一周(0803-0809) 或 1.第1周(0803-0809)
            folder_name = f"{week_idx}.第{week_str}周({start_mmdd}-{end_mmdd})"
            res = self._create_single_folder(folder_name)
            results.append(res)

        return results
