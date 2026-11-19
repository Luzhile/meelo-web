import fs from 'node:fs';import path from 'node:path';
const run=path.resolve(process.argv[2]);const read=p=>JSON.parse(fs.readFileSync(path.join(run,p),'utf8').replace(/^\uFEFF/,''));
const result=read('reports/ao-result.json');
// Correct the first-run metadata label without changing any measured value.
if('static_meshes_exported' in result){result.exported_room_meshes=result.static_meshes_exported;result.exported_static_meshes=result.static_objects;delete result.static_meshes_exported;fs.writeFileSync(path.join(run,'reports/ao-result.json'),JSON.stringify(result,null,2));}
const browser=read('reports/browser-ab-validation.json'),asset=read('reports/saved-asset-verification.json'),checks=read('reports/independent-ao-verification.json'),metrics=read('reports/screenshot-comparison.json'),provenance=read('reports/provenance.json');
const pct=x=>x.toFixed(4)+'%';
const text=`# MEELO 用餐房 AO 测试报告

日期：2026-11-19。输出目录：\`${run}\`。

## 结论

**AO 烘焙与网页绑定成功；严格 A/B 成立，但当前画面中实际视觉改善很轻微，不能宣称明显变好。**

AO=0 与原实时 PBR 在 ${browser.checks.width}×${browser.checks.height} 的 ${browser.checks.aVsAOZero.totalPixels} 个像素上完全相同。AO=0.5 时全画面 sRGB 通道均值下降约 ${pct(-browser.checks.aVsAOHalf.brightnessChangePercent)}，房间内部裁剪下降约 ${pct(-metrics.half.room.mean_srgb_change_percent)}。接触区域存在可测的轻微暗化，未形成显著的家具重量感提升。

没有把测试结果应用到主项目，没有批量处理其他房间，没有重新烘焙学习房，也没有提高环境光、改变曝光、给 Base Color 乘 AO 或添加其他视觉特效。

## 1. 开始前核实的状态

实际读取了 pipeline.py、study-04/REPORT.md、prepared-eight-rooms.blend，以及现有验证页与 Three r160 的 AO shader 实现。

- 准备文件：\`${provenance.prepared}\`。
- 原 prepared SHA-256：\`${provenance.prepared_sha256}\`。
- 用餐房有 221 个静态 Mesh、26 个动态 Mesh（含小猫、冰箱门、锅盖、水龙头等）。
- 所有静态对象已有 UV_Lightmap；使用原图集，1024² 像素中心检测无越界/重叠，原图集间距 8px。
- 材质已经按房间与静态/动态隔离，参与本轮的 23 个材质都属于用餐房静态组，旧 Lightmap 节点数为 0。
- 学习房 Diffuse 是独立 assets/GLB/HDR 和独立网页流程。主项目 HTML/models 的哈希确认没有接入 study-04 的实验产物。

## 2. 复用、隔离与非破坏性

复用了旧管线的 owner/excluded、完整资产审计、UV 检查、Cycles 设备配置、对象选择、同机位相机及 GLB 命名/次级 UV 导出逻辑。没有调用 prepare_materials、prepare_uv、bake_study 或 Diffuse 重建流程。

- 新建 meal_ao.py，直接读取已有 prepared 副本，并在本实验目录再做逐字节输入快照。
- 泛化 pipeline.py 的 export_room，保留 export_study 归档适配器；新导出模式使用真实 occlusionTexture，不再把它作为 Lightmap 的运输占位。
- 旧 Diffuse 命令行及 run.ps1 默认禁止隐式运行，必须明确启用归档选项才会执行。当前入口改为 run-ao.ps1；这不是回滚资产管线。
- 旧 study-04 的全部文件、旧学习房验证页的原文件、原始 .blend、prepared 副本及主项目 HTML/models 均进行了本轮前后哈希验证。
- 保存后的 AO 工作副本中，${asset.mesh_count} 个原 Mesh 的父级、UV 层名、原渲染 UV 标志和 UV 浮点坐标哈希与输入完全一致。
- ${asset.old_packed_images_unchanged} 个原图像数据块的名称、路径、尺寸及打包内容哈希未变。八张旧 Lightmap 和学习房 Diffuse 文件未覆盖。
- 原基础材质、颜色、真实 Emission 默认值保留；新增 AO 目标节点不连接 Base Color、Emission 或任何源着色输出。

## 3. AO 烘焙参数

| 参数 | 本轮值 |
|---|---|
| 房间 | meal，用餐房 |
| 引擎/设备 | Cycles / ${result.device} |
| Bake Type | AO（Ambient Occlusion） |
| 分辨率 | 1024 × 1024 |
| 采样 | ${result.samples} |
| Margin | ${result.margin}px，EXTEND |
| 距离 | ${result.distance}m |
| 距离属性 | scene.world.light_settings.distance |
| 原生说明 | ${result.distance_property_description} |
| UV | 显式指定 UV_Lightmap，直接复用 |
| 参与对象/材质目标 | ${result.static_objects} / ${result.material_targets} |
| 排除动态对象 | ${result.excluded_dynamic_objects} |
| 烘焙耗时 | ${result.seconds.toFixed(1)} 秒 |
| Direct / Indirect / Color | 全部关闭，未执行这些 Bake Pass |

0.25m 约为 3.6m 房高的 7%，用于桌脚、柜底和墙地交界的局部遮蔽，不让整间房互相长距离压暗。输出保留 AO 原始浮点 EXR 和网页 PNG。

采用白色空白背景并关闭清黑，配合 8px 扩边，避免图集空白区通过线性过滤形成黑缝。没有对最终画面做模糊、调色或额外 SSAO；本轮也没有对 AO 数据做跨 UV 岛模糊。256 样本用于控制采样颗粒。

AO 数据在 0–1 内，表面采样中位数为 ${result.surface_p50.toFixed(3)}；完全被包围/贴合的内部面可以为 0，不应把图集内部面的平均值误解为整幅房间会变暗的程度。PNG 与原始 EXR 的最大数值偏差 ${asset.png_exr_max_numeric_error.toFixed(6)}，符合 8 位量化，没有 AgX/gamma 烘入 AO。

## 4. 动态物件与静态遮挡

小猫、冰箱门、锅盖、水龙头等既不作为静态 AO 接收物，也不向静态环境烘入固定遮挡。它们在 A/B 两边都保留相同的实时 PBR 与阴影设置，因此不会出现“猫走开了地上还留一团 AO”的问题。

动态物件的近邻静态包围盒关系已记录在 dynamic-occlusion-evaluation.json；这是距离评估，不是精确碰撞检测。桌椅、固定柜体与墙地接触属于静态部分，正常参与烘焙。活动门、猫脚底等位置的动态接触效果仍受实时阴影能力限制，本轮没有用静态 AO 假装解决。

## 5. Three.js 严格 A/B

入口：http://127.0.0.1:5173/lightmap-validation/meal-ao/ 。原 /lightmap-validation/ 学习房归档不变，新页不加载学习房 GLB 或 HDR。

- A：实时 PBR，不使用 AO。
- B：同一实时 PBR，只增加新 aoMap 和 aoMapIntensity。
- 滑块范围 0–1，初始值 0.5；可平滑调节、关闭和重新开启。
- 实际纹理通道为 1，对应 uv1；NoColorSpace，flipY=false。所有静态绑定都已核对实际 GLB texCoord。
- ${browser.state.staticCount} 个静态 Mesh、${browser.state.dynamicCount} 个动态 Mesh；23 个静态材质绑定真实 AO，动态材质不绑定静态 AO。
- lightMap 数量为 0，没有旧 Lightmap 与 AO 重叠。
- GLB 保留 247 个用餐房 Mesh 及父子关系，保留 CAT_main、冰箱门、锅盖、水龙头等交互别名。
- 两种模式共用 ${browser.state.lights} 盏实时灯（5 个原房间灯具＋验证框架固定环境光），没有任何随模式/滑块改变的灯光代码。
- 相机位置/投影、曝光、色调映射、背景、模型变换/层级/可见性和非 AO 材质参数的完整快照一致；唯一允许变化的是 aoMap 和 aoMapIntensity。
- 曝光为 2^(-0.05)，AgX；基线沿用独立验证框架的 World 近似：中性环境色 linear [0.8,0.8,0.8]、强度 0.3。没有为了 AO 提高这个值。

这里的“原 PBR”指 prepared 资产的原基础材质和原房间灯具，经现有网页框架转换后的实时基线；它不是主游戏运行时全楼补光/CMF 重染的像素复刻。程序化 Blender 材质节点也受 core glTF 导出能力限制。这些限制在 A/B 两侧完全相同，不构成本轮差异来源。

## 6. 同机位截图与效果评估

| 文件 | 内容 |
|---|---|
| renders/meal-pbr.png | A，实时 PBR |
| renders/meal-pbr-ao-000.png | B，AO=0，与 A 像素完全一致 |
| renders/meal-pbr-ao-050.png | B，AO=0.5 |
| renders/meal-pbr-ao-100.png | B，AO=1 |
| renders/meal-ao-difference-x8.png | 仅用于定位差异，×8 放大，不是渲染效果 |

| 检查 | 结果 |
|---|---|
| A 与 AO=0 | ${browser.checks.aVsAOZero.differingPixels} 个不同像素 |
| AO=0.5 全画面平均变化 | ${pct(browser.checks.aVsAOHalf.brightnessChangePercent)} |
| AO=0.5 房间内部平均变化 | ${pct(metrics.half.room.mean_srgb_change_percent)} |
| AO=0.5 桌椅脚/地面区域平均变化 | ${pct(metrics.half.table_chair_floor.mean_srgb_change_percent)} |
| AO=0.5 柜底区域平均变化 | ${pct(metrics.half.cabinet_floor.mean_srgb_change_percent)} |
| AO=0.5 上部墙面平均变化 | ${pct(metrics.half.upper_wall.mean_srgb_change_percent)} |
| 新增近黑像素（原像素 >32/255，结果 <8/255） | ${metrics.new_near_black_pixels_half} |
| 网页 UV/加载错误 | ${browser.state.uvErrors.length} / ${browser.state.errors.length} |

这些是显示 sRGB 像素统计，不是光度学测量，也不代表“质量提升百分比”。本轮对比中未观察到上一轮那种密集墙面颗粒、大黑面或新增脏细线；原 CMF 参数保持一致，整幅没有明显变暗。但两张图肉眼非常接近，只能确认接触区域有轻微变化，不能宣称显著优化。

原因来自实际 Three r160 aomap_fragment：aoMap 缩放 indirectDiffuse，并在相应条件下影响间接镜面项，**不直接压暗直接灯光或真正的 Emission**。当前固定基线以直接面光/点光为主，所以 AO 的可见贡献有限。强度从 0.5 提到 1 的效果仍较轻微；本轮没有通过提高环境光、降低曝光、改材质或把 AO 乘入 Base Color 来强行放大。

## 7. 校验与边界

独立自动检查 ${checks.filter(c=>c.pass).length}/${checks.length} 项通过，详见 independent-ao-verification.json；保存后 Blender 验证见 saved-asset-verification.json；A/B GPU 回读和不变量验证见 browser-ab-validation.json；截图统计见 screenshot-comparison.json。

本轮只证明 AO 资产可正确生成、可控接入且 A/B 公平，不代表已经获得值得应用到主项目的视觉改善。继续保留此页作为实验，不把结果推广到其他房间、不进入 GI，也不更改全楼灯光。

## 修改的代码与新增资产

- pipeline.py：抽出共享 export_room，增加真实 AO 导出模式、导出代理清理和旧 Diffuse 入口保护；原 UV/材质准备实现保留。
- run.ps1：归档 Diffuse 默认停用。
- 新增 meal_ao.py、run-ao.ps1、meal_ao_viewer.html、verify_ao_asset.py、verify_ao.mjs、ao_image_metrics.py、make_ao_report.mjs。
- 新增当前实验的 assets、reports、blends、renders，以及 app/lightmap-validation/meal-ao/。
- 原始 .blend、prepared-eight-rooms.blend、study-04 全部文件、旧学习房验证页的原文件、主项目 HTML 和 models 未改。
`;
fs.writeFileSync(path.join(run,'REPORT.md'),text);
fs.writeFileSync(path.resolve('lightmap-pipeline/README.md'),`# MEELO 烘焙管线\n\n当前任务为 **用餐房 AO-only**；学习房 Diffuse 已归档，不继续烘焙。UV 和材质隔离成果保留。\n\n- [用餐房 AO 测试报告](runs/meal-ao-01/REPORT.md)\n- [归档：学习房 Diffuse 失败案例](runs/study-04/REPORT.md)\n- AO 预览：http://127.0.0.1:5173/lightmap-validation/meal-ao/\n- 学习房归档页：http://127.0.0.1:5173/lightmap-validation/\n\n重新进行独立 AO 测试：\n\n\`& './lightmap-pipeline/run-ao.ps1' -Samples 256 -Distance .25 -Margin 8\`\n\n每次输出全新目录，直接复用 prepared-eight-rooms.blend，不重展 UV、不重建材质隔离、不调用 Diffuse/GI/Color 烘焙。脚本不自动替换主项目。旧 run.ps1 与 pipeline.py 的 Diffuse CLI 默认受归档保护。\n\n本轮技术检查通过，但 AO 的视觉贡献很轻微，没有宣称显著改善，也没有推广其他房间。\n`);
console.log('AO_REPORT_WRITTEN',path.join(run,'REPORT.md'));
