# 当前工程状态与开发地图

交接基准：2026-11-20；用餐房最后确认的宽面补光响应为 70%。两个包的 `app/` 应具有完全相同的文件哈希。

## 唯一的当前入口

`app/index.html` 同时承载样式、界面、Three.js 场景、计时/清单/复盘、房间交互和浏览器降级。当前没有 Vite，不必自行添加框架迁移。Web 静态构建只复制当前 `app/index.html` 和 models、vendor、fonts、board。

初始化默认两层：学习/工作、睡觉；仅对没有存档的新来源生效。网页数据使用 localStorage 的 `meelo-demo-v2`。换端口、域名、浏览器或清除站点数据都会改变/清空该来源存档。桌面窗口位置与猫配置另存于 Electron userData，不包含在交接包。

## 模型资产来源与导出

- 原始资产：`assets/blender/meelo_unit_rooms_web-lighting-0.blend`，保留未修改备份。
- 当前编辑基础：`assets/blender/meelo_unit_rooms_realtime-clean.blend`。
- 两份模型的几何、顶点、面、对象名称、层级、变换、原有 UV 和 Blender 光源指纹一致。清理版只移除了八张旧 `LM_房间` 图像及相关 Image Texture 节点/连接；没有新增 `UV_Lightmap` 或重烘焙。
- 原有 `LM`/`UVMap` UV 保留，没有做逐面重叠检查；无 UV 的纯色对象不等于损坏。
- 当前导出采用原项目房间导出器，按 `Unit_房间` 归一化位置，保留 `CAT_main`、`I_`、`SHELL_`、`G_static`、`G_ceiling`。不要直接用 Blender 全场景导出来替换！那会造成房间漂浮、错位和交互名称丢失。
- 所有 .txt 模型是 GLB 二进制的 Base64 编码，不是直接可读网格；`rooms.json` 是房间局部灯光与相机元数据。

导出当前清理版：

```sh
blender --background --python tools/export-models.py
```

自定义输入输出：

```sh
blender --background --python tools/export-models.py -- --blend assets/blender/meelo_unit_rooms_realtime-clean.blend --out app/models
```

需要再次清理原始备份时，用不同输出文件：

```sh
blender --background assets/blender/meelo_unit_rooms_web-lighting-0.blend --python tools/clean_legacy_lightmaps.py -- assets/blender/your-clean-copy.blend
```

清理脚本禁止直接覆盖输入。保留真正灯管/屏幕的发光材质，不改 UV。原始模型包含指向旧电脑 F:/ 路径的窗景、电视图像引用，其中部分缺失；当前导出资源自包含，后续修改这些对象时需找回对应源纹理。

## 最终视觉设置

当前是原始 Blender 几何与现有网页 CMF 调整，加下午的八房间实时布光、柔和阴影和墙面上亮下暗 Shader 渐变。不是原始 Blender 渲染截图的逐像素还原。

- 八个 `ROOM_LIGHTING` 配置、`ROOM_FILL`、`ROOM_TUNE` 在 `app/index.html`，可按名称搜索。
- 用餐墙面/地板：`#D98C82`，金属度 0，粗糙度 1，不透明、双面、无颜色/法线贴图；墙面原微弱自发光为 `#3C0D03`，地板保留自己的 `#1E0401`。
- 用餐宽面光响应最后一次修改为 `mix(1.0, 0.70, uMealLighting)`。这与之前保留的 100% 材质钩子相乘；房间整体补光强度还受 `ROOM_LIGHTING.meal.front` 等因子影响，不应将“70%”理解为整栋灯光强度。
- 大楼总览修正系数 `TOWER_LIGHT_SCALE` 为 front .37、ambient 1.23。旧临时滑块 .339/.853 已被后续方案替代。
- 当前主阴影 2048²、房间聚光阴影 1024²，像素比上限 2，GTAO 强度 .28。应用户要求，早期降画质/建造时关闭 AO 等实验已回退。
- 旧 Emission Lightmap 转为 MeshBasicMaterial 的加载逻辑已移除；当前八房间运行时检查 Lightmap/baked 材质均为 0，实际灯管自发光仍存在。

## 当前交互修复

- 房间/大楼相机进出保留曲线过渡。
- 小猫乘电梯、走入房间完毕后才自动切近景；手动提前进房也不隐藏途中小猫。
- 大楼视角点击竣工：房间边框回弹、暖金描边、竣工章与四颗星星，约 1.1 秒清理，镜头不改动。减弱动画模式保留简化反馈。
- 左侧导航保持图标与 hover 文字；新建房间文字单行滚动；地下室使用整间点击热区；相关 UI 逻辑都在当前入口内。
- 浏览器的面板边框猫由 `makeRoofCat` 创建，仅打开面板且非减弱动画时显示；Electron 隐藏面板猫，使用系统桌面猫覆盖层。

## 性能与已知限制（不要误报已全部解决）

1. 顶部面光使用固定 8 槽灯池，共享补光/聚光灯放常驻灯架。盖楼或拆楼不会因这些光源数量变化而重新编译全场景 Shader。超过 8 层时优先分配当前房间和镜头附近楼层，较远楼层只保留其他照明；后续如要无限高楼全层一致，需设计另外的照明方案。
2. 房间实例池当前只在加载时准备每类两份原始场景克隆，不是完整的楼层回收池；取完后会回退即时 clone，墙面材质和 UI 等仍由 makeFloor 创建。
3. 同房型再次开工已测到灯数稳定、无数秒编译；首次使用未出现过的新房型仍可能有明显材质编译停顿。没有宣称彻底解决性能问题。
4. GTAO、高 DPI、实时阴影仍有持续 GPU 开销。清除旧烘焙后，部分原 MeshBasic 材质恢复 PBR 与阴影，成本和外观可能变化；必须以清理版重新测性能。
5. 源代码仍在大 HTML 中，缺少系统化自动测试；建议先建立固定机位截图和完整用户路径测试，再逐步拆模块。
6. 语音：网页使用浏览器 SpeechRecognition 支持与网络服务，不能保证所有浏览器/地区可用；桌面提供 Windows 语音输入桥。支持手动输入。
7. 浮空房间：Electron 为独立小岛窗口；网页为浏览器支持的画中画/页内降级，不能实现全系统桌面窗口扫描、透明置顶和鼠标穿透。
8. Electron 当前便携工程未签名、未制作安装器；Windows 平台代码依赖 Koffi/user32/dwmapi。Web 包不加载这些代码。

## 历史实验隔离

`archive/lightmap-experiments/` 保留审计、UV 管线、Diffuse/AO 实验脚本与学习房/用餐房报告；用于理解失败原因，不作为当前模型输入。为避免混淆，未携带旧实验的大体积 prepared/baked .blend 与输出贴图；文档保留原运行目录名称。

`assets/source-scripts/` 中是历史建模生成脚本，可研究结构，勿直接覆盖最新手工调整资产。`docs/` 的早期策划与项目报告描述可能包含设计目标或历史状态，请以本文件和当前源码为准。
