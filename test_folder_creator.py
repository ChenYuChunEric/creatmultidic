"""
test_folder_creator.py - FolderCreator 自動化單元測試腳本
"""

import os
import shutil
import unittest
from folder_creator import FolderCreator, int_to_chinese_number


class TestIntToChineseNumber(unittest.TestCase):
    def test_chinese_numbers(self):
        self.assertEqual(int_to_chinese_number(1), "一")
        self.assertEqual(int_to_chinese_number(2), "二")
        self.assertEqual(int_to_chinese_number(10), "十")
        self.assertEqual(int_to_chinese_number(11), "十一")
        self.assertEqual(int_to_chinese_number(20), "二十")
        self.assertEqual(int_to_chinese_number(25), "二十五")
        self.assertEqual(int_to_chinese_number(100), "一百")
        self.assertEqual(int_to_chinese_number(105), "一百零五")
        self.assertEqual(int_to_chinese_number(112), "一百一十二")


class TestFolderCreator(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath("./test_output")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.creator = FolderCreator(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_target_path_auto_create(self):
        nested_dir = os.path.join(self.test_dir, "nested", "sub_folder")
        self.creator.set_target_path(nested_dir)
        success, msg = self.creator.ensure_target_path_exists()
        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_dir))

    def test_create_custom_folders(self):
        names = ["專案A", "專案B", "專案C"]
        results = self.creator.create_custom_folders(names)
        self.assertEqual(len(results), 3)

        for res in results:
            self.assertEqual(res["status"], "created")
            self.assertTrue(os.path.exists(res["path"]))

        # 再次建立應顯示已存在
        dup_results = self.creator.create_custom_folders(names)
        for res in dup_results:
            self.assertEqual(res["status"], "exists")
            self.assertEqual(res["message"], "已存在")

    def test_create_sequential_folders_number_first(self):
        # 測試 01_專案, 02_專案... (補零至 2 位)
        results = self.creator.create_sequential_folders(
            base_name="專案", start_num=1, count=3, digits=2, number_first=True
        )
        self.assertEqual(results[0]["name"], "01_專案")
        self.assertEqual(results[1]["name"], "02_專案")
        self.assertEqual(results[2]["name"], "03_專案")
        for res in results:
            self.assertEqual(res["status"], "created")
            self.assertTrue(os.path.exists(res["path"]))

    def test_create_sequential_folders_name_first(self):
        # 測試 專案_001, 專案_002... (補零至 3 位，起始為 5)
        results = self.creator.create_sequential_folders(
            base_name="模組", start_num=5, count=2, digits=3, number_first=False, sep="-"
        )
        self.assertEqual(results[0]["name"], "模組-005")
        self.assertEqual(results[1]["name"], "模組-006")
        for res in results:
            self.assertEqual(res["status"], "created")

    def test_create_weekly_folders(self):
        # 起始日期 2026-08-03, 總週數 2 週 (國字)
        results = self.creator.create_weekly_folders("2026-08-03", 2, use_chinese_number=True)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "1.第一周(0803-0809)")
        self.assertEqual(results[1]["name"], "2.第二周(0810-0816)")

        for res in results:
            self.assertEqual(res["status"], "created")
            self.assertTrue(os.path.exists(res["path"]))

    def test_create_weekly_folders_arabic(self):
        # 起始日期 2026-08-03, 總週數 2 週 (阿拉伯數字)
        results = self.creator.create_weekly_folders("2026-08-03", 2, use_chinese_number=False)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "1.第1周(0803-0809)")
        self.assertEqual(results[1]["name"], "2.第2周(0810-0816)")

        for res in results:
            self.assertEqual(res["status"], "created")
            self.assertTrue(os.path.exists(res["path"]))

    def test_create_weekly_folders_invalid_date(self):
        with self.assertRaises(ValueError):
            self.creator.create_weekly_folders("2026/08/03", 2)


if __name__ == "__main__":
    unittest.main()
