# 放大房间天花板持续闪动

根因不是进房镜头动画。`updateLights()` 每帧把 HemisphereLight 强度设为 0.36 × daylightWeight；`applyMood()` 周期性将同一灯光改为 0.30 × daylightWeight × 房间 sky 系数。进房后两套更新互相覆盖，天花板在固定机位也会明暗交替。

排查证据：用餐房静止机位，补光强度在 0.36 与 0.195 交替，天花板同一像素红通道在 139 与 132 交替。关闭 GTAO、关闭天花板接收阴影、改为逐帧阴影，都没有消除跳变。相关数据保存在 ceiling-before.json、ceiling-no-ao.json、ceiling-no-receive.json、ceiling-every-shadow.json、ceiling-light-trace.json。

修复：仅由 updateLights 计算环境补光强度，合并原有房间系数、日照权重和关灯系数；applyMood 只更新天空状态，不再写同一灯光强度。没有改动灯型、顶部聚光参数、墙面渐变、材质或阴影开关。apply.cjs 已同步修正，避免重生成时再次引入。

实际连续渲染回归：

- 用餐房 40 帧：补光强度恒为 0.234，同一天花板像素红通道恒为 134。
- 睡觉房 30 帧：补光强度恒为 0.234，同一天花板像素红通道恒为 177。
- 保留原有 GTAO 与实时阴影，未发现 JavaScript / shader 错误。

验证使用独立 KEY 且禁止写存档的临时探针页面。页面源代码已归档在本目录，不保留额外产品 UI。
