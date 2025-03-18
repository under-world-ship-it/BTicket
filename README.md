# 🏸 北航羽毛球馆抢票自动化脚本

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen)

---

## 📦 环境依赖

### ❖ 核心组件
- Python 3.8+
- `requests` 库
- `selenium` 库

### ❖ 浏览器驱动
- selenium-chrome-driver 或 Edge 驱动  
  *（本项目`sources`目录已提供Edge驱动：`MicrosoftWebDriver.exe`）*

### ❖ 验证码识别
- [超级鹰打码平台](https://www.chaojiying.com/) 账号
  - 注册后需在配置文件中填写API密钥

---

## 🛠 驱动配置

### ✅ 配置步骤
1. 下载对应版本的浏览器驱动
2. 添加驱动路径到环境变量：
```bash
setx PATH "%PATH%;E:\project\sources"
```

---

## 🚀 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```
2. 修改 `resources/KeyConfig.yaml` 文件中的配置项
3. 运行 `main.py` 文件
## Warning:
目前本项目仍然在开发阶段,可能有小漏洞,可以注释掉main.py文件中_init_driver()实例方法中的"options.add_argument("--headless")"一句关闭无头模式,观察运行时的浏览器行为。
