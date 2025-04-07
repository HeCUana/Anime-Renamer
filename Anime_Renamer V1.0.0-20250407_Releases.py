import os
import re
import sys
import shutil
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QTextEdit, QMessageBox, QDialog, QDialogButtonBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QRegion, QPixmap

class AnimeOrganizer:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_anime_info(self, anime_name):
        """通过TMDB API获取动漫信息"""
        search_url = "https://api.themoviedb.org/3/search/tv"
        params = {
            "api_key": self.api_key,
            "query": anime_name,
            "include_adult": False,
            "language": "zh-CN"
        }
        
        response = requests.get(search_url, params=params)
        data = response.json()
        
        if data["total_results"] == 0:
            return None
        
        return data["results"]

    def get_seasons(self, anime_id):
        """获取动漫的季数信息"""
        details_url = f"https://api.themoviedb.org/3/tv/{anime_id}"
        params = {
            "api_key": self.api_key,
            "language": "zh-CN"
        }
        
        response = requests.get(details_url, params=params)
        data = response.json()
        
        seasons = []
        for season in data["seasons"]:
            if season["season_number"] != 0:  # 排除特殊集
                seasons.append({
                    "season_number": season["season_number"],
                    "name": season["name"]
                })
        
        return seasons

    def get_episode_info(self, anime_id, season_number, episode_number):
        """获取特定季和集的信息"""
        episode_url = f"https://api.themoviedb.org/3/tv/{anime_id}/season/{season_number}/episode/{episode_number}"
        params = {
            "api_key": self.api_key,
            "language": "zh-CN"
        }
        
        response = requests.get(episode_url, params=params)
        return response.json()

    def extract_episode_number(self, filename):
        """从文件名中提取集数"""
        patterns = [
            r'EP(\d+)',
            r'E(\d+)',
            r'第(\d+)集',
            r'(\d+)',
            r'(\d+)[a-zA-Z]*\.'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None

    def organize_anime_files(self, folder_path, selected_anime_id):
        """组织动漫文件"""
        folder_name = os.path.basename(os.path.normpath(folder_path))
        anime_name = re.sub(r'\s*\[[^\]]*\]\s*', '', folder_name)  # 去掉中括号内的内容
        anime_name = re.sub(r'\s*-\s*.*$', '', anime_name)  # 去掉破折号后面的内容
        
        if not selected_anime_id:
            return "未选择动漫"
        
        seasons = self.get_seasons(selected_anime_id)
        if not seasons:
            return "无法获取季数信息"
        
        # 创建季文件夹
        for season in seasons:
            season_folder = os.path.join(folder_path, f"Season {season['season_number']}")
            os.makedirs(season_folder, exist_ok=True)
        
        # 遍历文件夹中的所有文件
        file_info_list = []
        for file_path in Path(folder_path).glob('*'):
            if file_path.is_file():
                filename = file_path.name
                episode_number = self.extract_episode_number(filename)
                
                if episode_number is None:
                    continue
                
                target_season = None
                for season in seasons:
                    season_number = season['season_number']
                    episode_info = self.get_episode_info(selected_anime_id, season_number, episode_number)
                    
                    if episode_info.get('id'):
                        target_season = season
                        break
                
                if not target_season:
                    continue
                
                # 构建新文件名（保留原始后缀）
                file_suffix = file_path.suffix
                new_filename = f"S{target_season['season_number']:02d}E{episode_number:02d}{file_suffix}"
                if 'name' in episode_info:
                    new_filename = f"S{target_season['season_number']:02d}E{episode_number:02d} - {episode_info['name']}{file_suffix}"
                
                # 构建新文件路径
                season_folder = os.path.join(folder_path, f"Season {target_season['season_number']}")
                new_file_path = os.path.join(season_folder, new_filename)
                
                file_info_list.append({
                    "file_path": str(file_path),
                    "new_file_path": new_file_path,
                    "filename": filename,
                    "new_filename": new_filename,
                    "season_number": target_season['season_number'],
                    "episode_number": episode_number
                })
        
        # 处理字幕文件
        subtitle_info_list = []
        for file_path in Path(folder_path).glob('*'):
            if file_path.is_file():
                filename = file_path.name
                file_suffix = file_path.suffix.lower()
                
                # 检查是否为字幕文件
                if file_suffix in ['.txt', '.srt']:
                    episode_number = self.extract_episode_number(filename)
                    
                    if episode_number is None:
                        continue
                    
                    target_season = None
                    for season in seasons:
                        season_number = season['season_number']
                        episode_info = self.get_episode_info(selected_anime_id, season_number, episode_number)
                        
                        if episode_info.get('id'):
                            target_season = season
                            break
                    
                    if not target_season:
                        continue
                    
                    # 构建新字幕文件名
                    if file_suffix == '.txt':
                        new_subtitle_suffix = '.ass'
                    else:
                        new_subtitle_suffix = file_suffix
                    
                    new_subtitle_filename = f"S{target_season['season_number']:02d}E{episode_number:02d}{new_subtitle_suffix}"
                    if 'name' in episode_info:
                        new_subtitle_filename = f"S{target_season['season_number']:02d}E{episode_number:02d} - {episode_info['name']}{new_subtitle_suffix}"
                    
                    # 构建新字幕文件路径
                    season_folder = os.path.join(folder_path, f"Season {target_season['season_number']}")
                    new_subtitle_file_path = os.path.join(season_folder, new_subtitle_filename)
                    
                    subtitle_info_list.append({
                        "file_path": str(file_path),
                        "new_file_path": new_subtitle_file_path,
                        "filename": filename,
                        "new_filename": new_subtitle_filename,
                        "season_number": target_season['season_number'],
                        "episode_number": episode_number
                    })
        
        return file_info_list, subtitle_info_list

class AnimeSelectionDialog(QDialog):
    def __init__(self, anime_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择动漫")
        self.selected_anime_id = None
        self.init_ui(anime_list)

    def init_ui(self, anime_list):
        layout = QVBoxLayout(self)
        
        label = QLabel("请选择正确的动漫:")
        layout.addWidget(label)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        for anime in anime_list:
            item = QListWidgetItem(anime['name'])
            item.setData(Qt.ItemDataRole.UserRole, anime['id'])
            self.list_widget.addItem(item)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            self.selected_anime_id = selected_item.data(Qt.ItemDataRole.UserRole)
            super().accept()

class BatchConfirmationDialog(QDialog):
    def __init__(self, file_info_list, subtitle_info_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("批量确认重命名")
        self.file_info_list = file_info_list
        self.subtitle_info_list = subtitle_info_list
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 表格显示文件信息
        self.table_widget = QTableWidget(len(self.file_info_list) + len(self.subtitle_info_list), 5)
        self.table_widget.setHorizontalHeaderLabels(["类型", "当前文件名", "新文件名", "集数", "季数"])
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        
        # 填充视频文件信息
        for row, file_info in enumerate(self.file_info_list):
            type_item = QTableWidgetItem("视频")
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 0, type_item)
            
            filename_item = QTableWidgetItem(file_info["filename"])
            filename_item.setFlags(filename_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 1, filename_item)
            
            new_filename_item = QTableWidgetItem(file_info["new_filename"])
            self.table_widget.setItem(row, 2, new_filename_item)
            
            self.table_widget.setItem(row, 3, QTableWidgetItem(f"第 {file_info['episode_number']} 集"))
            self.table_widget.setItem(row, 4, QTableWidgetItem(f"第 {file_info['season_number']} 季"))
        
        # 填充字幕文件信息
        for row, subtitle_info in enumerate(self.subtitle_info_list, start=len(self.file_info_list)):
            type_item = QTableWidgetItem("字幕")
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 0, type_item)
            
            filename_item = QTableWidgetItem(subtitle_info["filename"])
            filename_item.setFlags(filename_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 1, filename_item)
            
            new_filename_item = QTableWidgetItem(subtitle_info["new_filename"])
            self.table_widget.setItem(row, 2, new_filename_item)
            
            self.table_widget.setItem(row, 3, QTableWidgetItem(f"第 {subtitle_info['episode_number']} 集"))
            self.table_widget.setItem(row, 4, QTableWidgetItem(f"第 {subtitle_info['season_number']} 季"))
        
        # 自动调整列宽以适应内容
        self.table_widget.resizeColumnsToContents()
        
        layout.addWidget(self.table_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        batch_confirm_button = QPushButton("批量确认")
        batch_confirm_button.clicked.connect(self.accept)
        
        individual_confirm_button = QPushButton("逐个确认")
        individual_confirm_button.clicked.connect(self.individual_confirm)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(batch_confirm_button)
        button_layout.addWidget(individual_confirm_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.resize(800, 600)

    def individual_confirm(self):
        self.individual_confirmation = True
        self.accept()

class AnimeOrganizerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.organizer = None
        self.api_key = self.load_api_key()
        self.init_ui()

    def load_api_key(self):
        """从 api_key.txt 文件中加载 TMDB API 密钥"""
        try:
            with open("api_key.txt", "r") as file:
                api_key = file.read().strip()
                if not api_key:
                    raise ValueError("API密钥为空")
                return api_key
        except FileNotFoundError:
            QMessageBox.warning(self, "错误", "未找到 api_key.txt 文件，请确保该文件存在于当前目录中")
            sys.exit(1)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载 API 密钥时出错: {str(e)}")
            sys.exit(1)

    def init_ui(self):
        self.setWindowTitle("动漫文件组织工具")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 文件夹选择
        folder_layout = QHBoxLayout()
        folder_label = QLabel("选择文件夹:")
        self.folder_input = QLineEdit()
        browse_button = QPushButton("浏览")
        browse_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_button)
        layout.addLayout(folder_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.organize_button = QPushButton("组织文件")
        self.organize_button.clicked.connect(self.organize_files)
        button_layout.addWidget(self.organize_button)
        layout.addLayout(button_layout)

        # 状态显示
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.folder_input.setText(folder_path)

    def organize_files(self):
        folder_path = self.folder_input.text().strip()

        if not folder_path:
            QMessageBox.warning(self, "错误", "请选择文件夹")
            return

        folder_name = os.path.basename(os.path.normpath(folder_path))
        anime_name = re.sub(r'\s*\[[^\]]*\]\s*', '', folder_name)  # 去掉中括号内的内容
        anime_name = re.sub(r'\s*-\s*.*$', '', anime_name)  # 去掉破折号后面的内容

        self.organizer = AnimeOrganizer(self.api_key)
        anime_list = self.organizer.get_anime_info(anime_name)

        if not anime_list:
            QMessageBox.warning(self, "错误", "未找到匹配的动漫")
            return

        if len(anime_list) == 1:
            selected_anime_id = anime_list[0]['id']
        else:
            dialog = AnimeSelectionDialog(anime_list, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_anime_id = dialog.selected_anime_id
            else:
                self.status_text.append("未选择动漫，操作已取消")
                return

        file_info_list, subtitle_info_list = self.organizer.organize_anime_files(folder_path, selected_anime_id)

        if not file_info_list and not subtitle_info_list:
            self.status_text.append("没有需要处理的文件")
            return

        dialog = BatchConfirmationDialog(file_info_list, subtitle_info_list, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if hasattr(dialog, 'individual_confirmation') and dialog.individual_confirmation:
                # 逐个确认
                for row in range(dialog.table_widget.rowCount()):
                    type_item = dialog.table_widget.item(row, 0).text()
                    current_filename = dialog.table_widget.item(row, 1).text()
                    new_filename = dialog.table_widget.item(row, 2).text()
                    
                    reply = QMessageBox.question(
                        self,
                        "确认重命名",
                        f"是否重命名:\n类型: {type_item}\n当前文件名: {current_filename}\n新文件名: {new_filename}",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        if type_item == "视频":
                            file_info = file_info_list[row]
                            shutil.move(file_info["file_path"], file_info["new_file_path"])
                            self.status_text.append(f"已重命名: {current_filename} -> {new_filename}")
                        elif type_item == "字幕":
                            subtitle_info = subtitle_info_list[row - len(file_info_list)]
                            shutil.move(subtitle_info["file_path"], subtitle_info["new_file_path"])
                            self.status_text.append(f"已重命名: {current_filename} -> {new_filename}")
                    else:
                        self.status_text.append(f"已跳过: {current_filename}")
            else:
                # 批量确认
                for row in range(dialog.table_widget.rowCount()):
                    type_item = dialog.table_widget.item(row, 0).text()
                    new_filename = dialog.table_widget.item(row, 2).text()
                    
                    if type_item == "视频":
                        file_info = file_info_list[row]
                        file_info["new_filename"] = new_filename
                        file_info["new_file_path"] = os.path.join(
                            os.path.dirname(file_info["new_file_path"]),
                            new_filename
                        )
                        shutil.move(file_info["file_path"], file_info["new_file_path"])
                        self.status_text.append(f"已重命名: {file_info['filename']} -> {new_filename}")
                    elif type_item == "字幕":
                        subtitle_info = subtitle_info_list[row - len(file_info_list)]
                        subtitle_info["new_filename"] = new_filename
                        subtitle_info["new_file_path"] = os.path.join(
                            os.path.dirname(subtitle_info["new_file_path"]),
                            new_filename
                        )
                        shutil.move(subtitle_info["file_path"], subtitle_info["new_file_path"])
                        self.status_text.append(f"已重命名: {subtitle_info['filename']} -> {new_filename}")
        else:
            self.status_text.append("操作已取消")

        self.status_text.append("文件组织完成！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimeOrganizerUI()
    window.show()
    sys.exit(app.exec())