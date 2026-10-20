# CCTV Headquarters 外观模型 · 凹槽幕墙修订版 v2

Blender 4.3.2 无头模式与 bpy 生成的中央电视台总部大楼外观重建。

本次将外凸斜杆替换为实际切入幕墙的斜交凹槽：槽底低于玻璃 30 mm，细分格缝下沉 3 mm；交叉处先合并，再生成槽底、槽壁和小倒角。局部射线测量已验证凹入深度。

## 下载

- [下载最新版完整交付包](https://github.com/wikipiggy/CCTV/raw/refs/heads/main/output/CCTV_download.zip)：模型、完整脚本、几何数据和六张新渲染图。
- [单独下载 Blender 模型](https://github.com/wikipiggy/CCTV/raw/refs/heads/main/output/CCTV_Headquarters.blend)
- [bpy 主脚本](output/build_cctv.py) · [凹槽生成算法](output/generate_recessed_facade.py) · [建模说明与精度限制](output/README_zh.md)

## 玻璃表面特写 · 2000×2000

### 交叉节点：玻璃切口、槽底与倒角
![玻璃交叉节点特写](output/renders/05_closeup_glass_junction_denoised.png)

### 斜视：槽壁、内凹深度与玻璃反射
![玻璃凹槽斜视特写](output/renders/06_closeup_glass_grazing_denoised.png)

## 更新后的全景 · 1800×1800

![正面](output/renders/01_front_hero_denoised.png)
![俯视](output/renders/02_aerial_denoised.png)
![右侧](output/renders/03_right_oblique_denoised.png)
![仰视](output/renders/04_soffit_denoised.png)

主体外壳 234 m。槽深、水平尺寸、网格排布及周边环境包含参考图估算与简化，不是实楼测量数据或施工图复刻。
