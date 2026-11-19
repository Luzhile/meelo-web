import fs from 'node:fs';import path from 'node:path';
const dir=path.resolve(process.argv[2]);const read=p=>JSON.parse(fs.readFileSync(path.join(dir,p),'utf8').replace(/^\uFEFF/,''));
const original=read('reports/audit-original.json'),isolation=read('reports/material-isolation.json'),bake=read('reports/study-bake.json'),gltf=read('reports/gltf-validation.json'),images=read('reports/image-comparison.json'),checks=read('reports/independent-verification.json'),browser=read('reports/browser-validation.json'),provenance=read('reports/provenance.json'),exact=read('reports/exact-uv-verification.json');
const rows=Object.entries(original.summary).map(([room,s])=>{const uv=read(`reports/uv-${room}.json`);return `| ${room} | ${s.static||0} | ${(s['dynamic-cat']||0)+(s['dynamic-interaction']||0)} | ${(uv.occupancy_ratio*100).toFixed(1)}% | ${uv.actual_island_margin_pixels}px |`;}).join('\n');
const pct=x=>(x*100).toFixed(2)+'%';
const text=`# MEELO Lightmap 管线重构交付报告

日期：2026-11-19。正式结果目录：\`${dir}\`。

## 结论与验收边界

已完成非破坏式审计、材质隔离、八房间 UV 重建、学习房单独测试和独立 Three.js 加载验证。${checks.filter(c=>c.pass).length}/${checks.length} 项独立工程检查通过。

**视觉尚未达到正式替换主项目的门槛。** 1024²、32 样本仍有噪点和细小边缘/接缝发暗；浏览器与 Blender 的显示变换和着色器也有差异。因此没有替换主预览，没有烘焙其余七房。工程可用不等于视觉已经验收。

## 1. 资产审计与隔离

- 输入：\`${provenance.source}\`。
- SHA-256：\`${provenance.sha256}\`。原件和逐字节备份哈希一致，原件结束时再次验证未变。
- 全量记录 ${original.objects.length} 个 Mesh；${original.unassigned.length} 个无法确定房间归属的对象单列在 audit-original.json/unassigned，未自动分配或烘焙。
- 发现 ${Object.keys(original.shared_between_rooms).length} 组跨房间共享材质。为有效房间按“房间＋静态/动态”复制 ${isolation.material_copies} 个材质数据块，旧家具及原始材质保留。
- 从复制后的材质节点图隔离 ${isolation.removed_legacy_nodes.length} 个旧 Lightmap Image Texture 节点。隔离涵盖 Base Color、Emission 及嵌套 Group；原始贴图数据块、旧文件均未覆盖或删除。
- 保留 Principled/Emission 的原始默认值和真实发光源，原始程序化基础色、Noise/Bump/Roughness 等其余节点保留。独立检查比较了复制前后的这些默认参数。
- 保留源对象名称和父子层级；工作副本在创建新 UV 前求值倒角，保持可见形状，原文件和源 Mesh 均在备份内。完整修改记录和节点连接见 audit-original.json、audit-repaired.json、material-isolation.json。
- 原来的 LM_* UV 层和原始纹理映射不删除。无 UV 的静态对象创建 UV_Original 占位，再新增 UV_Lightmap。未给小猫和可动物件生成烘焙 UV。

## 2. UV 图集

每个房间独立打包，全房间联合归一化岛屿面积，并对墙地/主体家具加视觉重要性权重。下面的占用率和间距对应 1024² 测试尺度，不是最终分辨率承诺。

| 房间 | 静态对象 | 动态对象/猫 | 图集有效像素占比 | 图集间距 |
|---|---:|---:|---:|---:|
${rows}

八房间均无越界，1024² 像素中心三角形检测无重复占用。还额外运行 Blender 原生重叠选择和逐三角形正面积裁剪（阈值 1e-12 UV 面积）。裁剪未发现正面积重叠。

原生选择器对用餐房/学习房的退化倒角三角形有告警，已单独记录，并没有忽略告警后宣称通过。学习房有 ${exact.studyWork.zero_area_triangles} 个极小/零 UV 面积三角形，其中 ${exact.studyWork.zero_geometry_triangles} 个本身是零面积几何；其余对应的总空间面积约 ${exact.studyWork.collapsed_uv_surface_area.toExponential(3)}。本次未删改这些源几何。详细数值见 native-uv-verification.json、exact-uv-verification.json。

## 3. 学习房烘焙测试

- 仅 studyWork，${bake.static_objects} 个静态对象，${bake.target_materials} 个独立材质目标。
- Cycles ${bake.device}，${bake.resolution}×${bake.resolution}，${bake.samples} 样本。
- Diffuse，DIRECT＋INDIRECT，关闭 COLOR。**显式指定 uv_layer='UV_Lightmap'**，不依赖活动渲染 UV 的默认行为。
- 当前图集间距 2px，Bake 扩边 ${bake.bake_margin_pixels}px。它是低清管线测试的折衷，不能据此判定最终细缝质量。
- 烘焙约 ${bake.seconds.toFixed(1)} 秒；像素有限、非全黑，峰值 ${bake.pixel_max.toFixed(3)}。峰值大于 1，故保留线性浮点 EXR/HDR，不能直接裁剪成普通 8 位 JPG。
- 参与计算的复制材质中旧 Lightmap 节点数：${bake.legacy_nodes_in_bake_materials}。动态小猫和会移动的物件不在烘焙/对比参考里投下固定阴影。
- 对照沿用源房间有效灯光和原 World；场景级无归属/校准灯不会盲目叠加到所有房间，study-isolation.json 列出实际启用清单。
- 样本路径：renders/study-reference.png（清理后的原 PBR），study-baked-reconstruction.png（底色×Diffuse 光照＋真实 Emission），study-difference-x4.png，study-uv-atlas.png，study-lightmap-preview.png。

第一次测试因 Cycles 使用了错误默认 UV 出现黑块，已在显式 UV 测试中修复。旧失败结果保存在其他 run 目录，正式交付以本目录为准。

## 4. GLB 与 Three.js 加载验证

- 导出 ${gltf.source_meshes}/${gltf.exported_meshes} 个原学习房有效 Mesh，无缺失，保留原父子关系和 source_object 元数据。
- 保留 CAT_main、I_studyWork_*、SHELL_studyWork_* 兼容名称；原 Blender 名称留在 extras，工作 .blend 中不改名、不合并家具。
- 验证每个静态 primitive 的次级 UV。使用 glTF occlusionTexture 作为明确的 UV 通道运输标记；**它不是真正 AO**。加载后移除 aoMap，改为独立 HDR lightMap。
- texture.channel=1、NoColorSpace（线性 HDR）、flipY=false、lightMapIntensity=π。Three r160 的标准材质把 lightMap 当作 irradiance 使用，π 用于与 Cycles 无 Color 的漫反射结果对应；不是额外补灯。
- 静态与动态使用独立渲染层/两次保留深度的渲染：烘焙静态不再接收实时直接灯，小猫/可动物件仍保留 PBR 和实时灯。不会同时叠加原房间直接漫反射与烘焙直接光。
- 浏览器读取到 ${browser.state.staticCount} 个静态 primitive、${browser.state.dynamicCount} 个动态 primitive，UV 错误 ${browser.state.uvErrors.length}，加载错误 ${browser.state.errors.length}；多材质 glTF Group 的静态标记已正确继承。
- 已验证“烘焙／实时 PBR”切换和动态物件显示，并通过实际射线拾取命中 I_studyWork_screen。独立验证页不是对整套计时/派对/开关灯业务逻辑的替代；生产交互逻辑未改。
- 预览：http://127.0.0.1:5173/lightmap-validation/ 。主页面及全部原 models 文件的哈希均保持原样。

## 5. 同机位差异

采用同一正交相机、位置、目标及 900×600 画幅。下表只统计房间内部裁剪，排除 World 与网页背景不同带来的误差。MAE 是 sRGB 通道绝对误差除以 1 的比例，**不是相似度或主观质量评分**。

| 对比 | 房间内 MAE |
|---|---:|
| Blender 烘焙重建 vs Blender 原 PBR | ${pct(images.blender_diffuse_bake_vs_clean_pbr.mae_srgb_room_crop)} |
| Three.js 烘焙 vs Blender 烘焙重建 | ${pct(images.web_lightmap_vs_blender_baked.mae_srgb_room_crop)} |
| Three.js 烘焙 vs Blender 原 PBR | ${pct(images.web_lightmap_vs_blender_reference.mae_srgb_room_crop)} |
| Three.js 实时对照 vs Blender 原 PBR | ${pct(images.web_realtime_vs_blender_reference.mae_srgb_room_crop)} |

剩余差异包括：32 样本噪点、低清图集的细岛与扩边不足、Diffuse 不包含视角相关镜面反射、核心 glTF 不导出程序化 Noise/Bump、Three.js AgX 没有 Blender 的 Medium High Contrast Look，以及动态物件使用近似实时光照。网页两种模式只是光照路线对照，不能把网页实时结果当成 Blender 的精确复刻。

## 6. 后续七房计划与门槛

先修学习房视觉问题，再依次测试 **用餐 → 通勤 → 家居 → 户外 → 卧室 → 娱乐 → 社交**。本次没有执行此队列。

1. 学习房先把 32 样本升到 128–256，并评估 2048/4096 图集；清查微小岛，保证最终像素间距与扩边足够。当前 1024² 样片不直接上生产。
2. 用同机位检查墙角、柜底、百叶窗、书架和桌腿，不出现大黑面、串图、明显缝线；确认显示变换差异后再定视觉验收图。
3. 用餐/通勤/家居先验证普通静态房间流程；冰箱门、锅盖、车门、吸尘器等保持动态，不把它们的移动阴影画死。
4. 户外保留蝴蝶、苹果交互；卧室验证窗帘和关灯两种状态。单张固定光照图不能真实响应灯光关闭，应另做状态图或明确的光照混合策略。
5. 娱乐和社交最后处理。正常模式可以烘焙，但电视、派对、旋转灯效果必须留给动态层，不能假装一张静态贴图覆盖全部状态。
6. 每房独立新输出目录，核查原件哈希、UV 几何裁剪、材质目标隔离、HDR 像素、GLB TEXCOORD 和交互名称，再做网页同机位验收。
7. 只有样片视觉通过、交互状态策略明确后，才接入主项目。届时还需针对 G_ceiling/SHELL 等生产导出适配器验证入室、层高变化、关灯、刷新存档等完整流程。

## 文件入口

- 脚本：lightmap-pipeline/pipeline.py；可重复执行入口 run.ps1（每次必须新目录）。
- Blender：blends/original-backup.blend、prepared-eight-rooms.blend、study-baked.blend（后者刻意隔离到学习房）。
- 完整审计与机器测试：reports/ 下 JSON。
- 网页验证模板：lightmap-pipeline/viewer.html；部署到 app/lightmap-validation/，未触碰 app/index.html。
- 生产主项目尚未替换，没有新增全局调光面板。
`;
fs.writeFileSync(path.join(dir,'REPORT.md'),text);
fs.writeFileSync(path.join(path.dirname(path.dirname(dir)),'README.md'),`# MEELO Lightmap 管线\n\n当前交付：[study-04 报告](runs/study-04/REPORT.md)。\n\n预览：http://127.0.0.1:5173/lightmap-validation/\n\n原始 .blend 和生产主页面/模型未修改；只烘焙学习房。工程测试通过，低清样片尚未通过正式视觉验收，其余七房未烘焙。\n\n重新执行：在 PowerShell 运行 \`& './lightmap-pipeline/run.ps1' -Size 1024 -Samples 32\`。输出目录必须全新，脚本拒绝覆盖旧 run。需要本机 Blender 5.2 和项目自带 Node。\n\n脚本：\n\n- pipeline.py：备份、全量审计、隔离、八房 UV、学习房烘焙和 GLB 导出。\n- check_prepared.py / exact_overlap.py：原生 UV 检查及三角形精确裁剪复核。\n- verify.mjs：独立校验原件/主项目哈希、层级、UV、发光参数和 GLB。\n- viewer.html：线性 HDR Lightmap 与动态 PBR 分层验证。\n- image_metrics.py：同机位差异测量（需要先生成浏览器截图）。\n\n不能直接复用旧 bake_reference.py，也不能在网页里给静态烘焙对象重复叠原直接灯。\n`);
console.log('REPORT_WRITTEN',path.join(dir,'REPORT.md'));
