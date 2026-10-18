# CCTV 总部外观重建

本项目通过 Blender 4.3.2 无头模式、bpy 和 Cycles 创建可编辑外观模型。坐标单位为米，X 东、Y 北、Z 上。

## 运行

```bash
cd /workspace/CCTV/output
blender -b -t 5 --python build_cctv.py -- --stage massing --samples 12
blender -b -t 5 --python build_cctv.py -- --stage final --samples 64
```

`progress/` 保存形体检查图；`renders/` 保存最终视角；模型不依赖外部贴图。

## 参考与精度界限

依据用户提供的两张剖立面、一张 F41 层平面、场地总图以及多角度照片进行参数化视觉重建。不是测绘模型、施工图模型或结构分析模型。图纸缺少可读的水平尺寸、全部立面网格节点坐标与准确地理配准，因此水平尺寸、局部幕墙分格、节点、周边道路宽度和城市背景为估算。斜交疏密为程序化近似，不宣称逐根对应实楼。

主体控制标高：0、46.45、161、234 m；低塔屋面控制约 213.9 m。237.5 m 用作顶部附属构件上限。两塔位于平面西北与东南，高空连接沿西与南两条边，底部连接沿北与东两条边，构成空间闭环。平面外包 152 m，塔楼名义宽 44 m，均为比例估算。

水平随高度缩放：`x(z)=x0*(1-0.32*z/234)`，`y(z)=y0*(1-0.32*z/234)`。固定高度截面保留方形，各塔轴线沿对角线向场地内侧偏移。屋面从西侧 234 m 向东侧 213.9 m 变化。所有外壳面由同一参数映射生成，避免独立塔体与悬挑错位。

幕墙采用独立面板材质差异、实体细框及主次斜撑；没有内部楼层、办公室、完整结构节点。悬挑底部圆形构件表现为暗色圆形嵌件，不是贯通实体布尔孔。TVCC、城市建筑、植被和景观为背景体量表达。

最后一张 3d66 效果图仅作辅助视角，以实景照片优先。输出真实性应结合最终渲染判断，不等同于照片级测量复刻。

## 渲染与文件

最终生产使用 Cycles CPU、1800×1800 像素、每视角采样上限 64，自适应阈值 0.065、最小采样 16。当前 Blender 没有内置 OpenImageDenoise，因此内置降噪关闭。`denoise.py` 使用单独安装的 OIDN CPU 库处理 PNG，保留原始图并输出 `_denoised.png`；在显示空间处理，无辅助法线/反照率通道，细线可能被轻微软化。可用更高采样重新渲染进一步改善细节。

可选降噪依赖安装：

```bash
python -m pip install --target /workspace/library-files/oidn -r requirements-render.txt
python denoise.py renders/01_front_hero.png renders/02_aerial.png renders/03_right_oblique.png renders/04_soffit.png
```

主要交付：`CCTV_Headquarters.blend`、`build_cctv.py` 与其辅助文件 `urban_details.py`。`validation.json` 保存重开模型后的几何与资源检查结果。其他辅助脚本及 `progress/` 记录实际检查、修改和渲染过程。`cctv_massing.blend` 是第一次形体检查版本，最终应使用大写名称的 `CCTV_Headquarters.blend`。

幕墙玻璃使用反射型简化着色，未模拟双层玻璃和室内折射结构。树木、车辆及城市背景为程序化简化资产。本交付不应被描述为逐节点精确或与实景无法区分的摄影级复刻。
