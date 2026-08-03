"""
gui.pyw - GUI 視窗直接啟動點 (雙擊即可執行，不開啟 CMD 視窗)
"""
from gui import FolderCreatorGUI

if __name__ == "__main__":
    app = FolderCreatorGUI()
    app.mainloop()
