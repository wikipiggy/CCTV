# CCTV 总部外观重建 · 凹槽幕墙修订版 v2

通过 Blender 4.3.2 无头模式、bpy 和 Cycles 创建的可编辑外观模型。米制，X 东、Y 北、Z 上；主体外壳 234 m，顶部附属平台约 237.5 m。

## 此次修正

- 删除原来的外置斜杆、凸起细框和外凸边框。
- 以玻璃外表面为 0 基准，真实切去斜交网格带所在的玻璃区域。
- 主、次斜线先求二维并集，再统一生成槽底、槽壁和倒角；交叉处不叠杆。
- 深色槽底位于 -30 mm，槽口倒角宽 8 mm、下沉 6 mm；细分格缝宽 35 mm、深 3 mm。
- 次级斜线终点落在主线交点上，不再悬空截断。
- 局部射线检查证实槽底约低于玻璃 30 mm。几何面域覆盖检查通过，未采用把杆件藏到完整玻璃后面的替代做法。
- 新增交叉节点特写和斜视凹槽特写，均为 2000×2000；四张全景更新为 1800×1800。

以上凹槽深度、宽度与倒角是根据照片调试的视觉重建参数，不是实楼测量尺寸。

## 文件与重建

`CCTV_Headquarters.blend` 是最新版；包含六个相机，材质与天空无需外部贴图。

```bash
cd /path/to/output
blender -b -t 5 --python build_cctv.py -- --stage final --samples 64
python denoise.py renders/01_front_hero.png renders/02_aerial.png renders/03_right_oblique.png renders/04_soffit.png renders/05_closeup_glass_junction.png renders/06_closeup_glass_grazing.png
```

主脚本读取随包提供的 `recessed_facade_geometry.json.gz`，通过 `load_recessed_facade.py` 安装切割后的玻璃及凹槽，因此不要求 Blender 内安装 Shapely。

如需调整槽深、宽度或网格形状，先编辑 `generate_recessed_facade.py`，然后使用宿主 Python 重新生成几何：

```bash
python -m pip install shapely
python generate_recessed_facade.py
```

`urban_details.py` 是主脚本调用的道路附属资产脚本。`render_recessed_revision.py` 可对已打开的最新版模型输出六张正式图；`validate_recessed_facade.py` 执行射线深度、相机数与高度检查。

当前 Blender 不含内置 OIDN，因此关闭内置降噪；`denoise.py` 使用单独安装的 OIDN CPU 库，保留原始 PNG 并写出 `_denoised.png`。安装可选降噪依赖：`python -m pip install -r requirements-render.txt`。显示空间降噪可能轻微软化细线，可查看原始图或提高采样。

## 参考及精度范围

依据用户提供的两张剖立面、F41 层平面、场地总图和多角度照片重建。控制标高为 0、46.45、161、234 m；低端屋面约 213.9 m。平面外包 152 m、塔楼名义宽 44 m，为比例估算。两塔位于西北与东南，上部沿西、南两边连接，下部沿北、东两边连接，形成空间闭环。

水平位移使用参数层高的线性缩放，屋面另行映射为有高差的截面。水平尺寸、逐根斜撑节点、玻璃分格及城市环境仍有估算与简化；没有内部楼层和办公室。悬挑底面圆形构件为嵌件表现，不是贯通孔。玻璃为反射型简化着色，周边城市、车辆与植被为程序化资产。本模型不是测绘级、施工图级或照片级复刻。
