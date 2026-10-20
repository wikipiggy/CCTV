# CCTV Headquarters 外观模型 · 凹槽幕墙修订版 v3

Blender 4.3.2 无头模式与 bpy 生成的中央电视台总部大楼外观重建。

本版按用户指定将斜交凹槽加深到 200 mm。槽底、槽壁和槽口倒角统一使用独立的深灰哑光涂层材质，关闭镜面高光与清漆反射；细分格缝仍为 3 mm。

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

主体外壳 234 m。槽深按用户指定设为 200 mm；水平尺寸、网格排布及周边环境仍包含参考图估算与简化。
