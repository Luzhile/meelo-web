# MEELO 烘焙管线

当前任务为 **用餐房 AO-only**；学习房 Diffuse 已归档，不继续烘焙。UV 和材质隔离成果保留。

- [用餐房 AO 测试报告](runs/meal-ao-01/REPORT.md)
- [归档：学习房 Diffuse 失败案例](runs/study-04/REPORT.md)
- AO 预览：http://127.0.0.1:5173/lightmap-validation/meal-ao/
- 学习房归档页：http://127.0.0.1:5173/lightmap-validation/

重新进行独立 AO 测试：

`& './lightmap-pipeline/run-ao.ps1' -Samples 256 -Distance .25 -Margin 8`

每次输出全新目录，直接复用 prepared-eight-rooms.blend，不重展 UV、不重建材质隔离、不调用 Diffuse/GI/Color 烘焙。脚本不自动替换主项目。旧 run.ps1 与 pipeline.py 的 Diffuse CLI 默认受归档保护。

本轮技术检查通过，但 AO 的视觉贡献很轻微，没有宣称显著改善，也没有推广其他房间。
