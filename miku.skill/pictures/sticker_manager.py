#!/usr/bin/env python3
"""
Miku Hermes Chat — 可视化表情包管理系统
=============================================
功能：上传 / 删除 / 分类管理 初音未来表情包
启动：python sticker_manager.py
访问：http://localhost:5100

背景壁纸：每 5 分钟自动循环切换 pictures/background/ 中的图片
"""

import json
import os
import shutil
import uuid
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, send_file

BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "sticker_catalog.json"
BG_DIR = BASE_DIR / "background"

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")


# ============================================================
# 工具函数
# ============================================================
def load_catalog():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_catalog(data):
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def scan_image_files():
    """扫描所有图片文件路径"""
    images = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.bmp"):
        for img in BASE_DIR.rglob(ext):
            rel = str(img.relative_to(BASE_DIR)).replace("\\", "/")
            if "background" not in rel:
                images.append(rel)
    return sorted(images)


def scan_backgrounds():
    """扫描 background 目录中的壁纸"""
    if not BG_DIR.exists():
        return []
    bgs = []
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        for img in BG_DIR.glob(ext):
            bgs.append(f"background/{img.name}")
    return sorted(bgs)


# ============================================================
# API 路由
# ============================================================
@app.route("/api/catalog", methods=["GET"])
def api_get_catalog():
    try:
        data = load_catalog()
        data["_backgrounds"] = scan_backgrounds()
        data["_all_images"] = scan_image_files()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/catalog", methods=["POST"])
def api_save_catalog():
    try:
        data = request.get_json()
        save_catalog(data)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """上传表情包图片"""
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "no file"}), 400

        original_name = file.filename or "sticker.png"
        ext = Path(original_name).suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
            return jsonify({"error": f"unsupported format: {ext}"}), 400

        source = request.form.get("source", "uploaded")
        safe_name = f"{uuid.uuid4().hex[:8]}_{original_name}"

        if source in ("01_miratsu",):
            dest_dir = BASE_DIR / source
        elif source.startswith("06_"):
            dest_dir = BASE_DIR / "06_bilibili_200" / "miku_only" / source
        else:
            dest_dir = BASE_DIR / "uploaded"
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / safe_name
        file.save(str(dest_path))

        rel_path = str(dest_path.relative_to(BASE_DIR)).replace("\\", "/")
        return jsonify({"ok": True, "path": rel_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete", methods=["POST"])
def api_delete():
    """删除表情包图片"""
    try:
        data = request.get_json()
        img_path = data.get("path", "")
        target = BASE_DIR / img_path

        # 安全检查
        try:
            target.resolve().relative_to(BASE_DIR.resolve())
        except ValueError:
            return jsonify({"error": "invalid path"}), 403

        if target.exists() and target.is_file():
            os.remove(str(target))
            return jsonify({"ok": True})
        return jsonify({"error": "file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/backgrounds", methods=["GET"])
def api_backgrounds():
    return jsonify({"backgrounds": scan_backgrounds()})


@app.route("/api/add-category", methods=["POST"])
def api_add_category():
    """添加新分类"""
    try:
        data = request.get_json()
        cat_name = data.get("name", "").strip()
        if not cat_name:
            return jsonify({"error": "name required"}), 400

        catalog = load_catalog()
        if cat_name in catalog["categories"]:
            return jsonify({"error": f"category '{cat_name}' already exists"}), 409

        catalog["categories"][cat_name] = {
            "\u60c5\u7eea": "",
            "\u89e6\u53d1\u8bcd": [],
            "\u89e6\u53d1\u573a\u666f": [],
            "stickers": []
        }
        save_catalog(catalog)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete-category", methods=["POST"])
def api_delete_category():
    try:
        data = request.get_json()
        cat_name = data.get("name", "").strip()
        catalog = load_catalog()
        if cat_name in catalog["categories"]:
            del catalog["categories"][cat_name]
            save_catalog(catalog)
            return jsonify({"ok": True})
        return jsonify({"error": "category not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/update-category", methods=["POST"])
def api_update_category():
    try:
        data = request.get_json()
        cat_name = data.get("name", "").strip()
        catalog = load_catalog()
        if cat_name not in catalog["categories"]:
            return jsonify({"error": "category not found"}), 404

        cat = catalog["categories"][cat_name]
        if "emotion" in data:
            cat["\u60c5\u7eea"] = data["emotion"]
        if "triggers" in data:
            cat["\u89e6\u53d1\u8bcd"] = [w.strip() for w in data["triggers"] if w.strip()]
        if "scenes" in data:
            cat["\u89e6\u53d1\u573a\u666f"] = [s.strip() for s in data["scenes"] if s.strip()]
        save_catalog(catalog)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# 主页
# ============================================================
@app.route("/")
def index():
    return send_file(str(BASE_DIR / "sticker_manager.html"))


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 52)
    print("  初音未来 表情包可视化管理系统")
    print(f"  启动地址: http://localhost:5100")
    print(f"  数据文件: {CATALOG_PATH}")
    print(f"  壁纸目录: {BG_DIR}")
    print("  按 Ctrl+C 关闭服务器")
    print("=" * 52 + "\n")
    app.run(host="127.0.0.1", port=5100, debug=False)