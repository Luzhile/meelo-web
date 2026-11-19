# MEELO Web 开发交接包 · 2026-11-20

这是可继续编辑、构建和导出模型的完整工作包。入口是 `app/index.html`，不是根目录的展示 HTML。

## 开始开发

安装 Node.js 20 或更新版本，在本目录运行：

```sh
npm install
npm run dev
```

打开 http://127.0.0.1:5173/ 。前端为原生 HTML/JavaScript + Three.js r160，未使用 Vite；Three.js 通过本地 importmap 引入，无需联网 CDN。编辑 `app/index.html` 后刷新浏览器。

```sh
npm run build:web
npm run preview:web
```

第二条命令在 http://127.0.0.1:4173/ 提供生成的 `dist/`。

## Vercel / GitHub

本包内容直接作为仓库根目录：Root Directory 留空/仓库根，Framework 为 Other，Build Command 为 `npm run build:web`，Output Directory 为 `dist`。不用提交 `dist` 和 `node_modules`。

需要提交 `app/`、`tools/`、`package.json`、`package-lock.json`、`vercel.json`、`.vercelignore`、`.gitignore`、`README.md`。继续资产开发时也应交接 `assets/`、`docs/`、`archive/`；它们不进入静态构建。可用 Git LFS 管理 Blender 二进制文件，但本地导出前先拉取真实文件。

## 内容导航

- `app/`：最新主界面源码、八房间模型、材质、字体、UI 图像和本地 Three.js 源文件。
- `tools/`：开发/预览服务器、Web 构建、Blender 导出、旧 Lightmap 清理和资产审计脚本。
- `assets/blender/`：当前清理版 Blender 和原始模型备份，两者几何、层级、UV 一致。
- `assets/export/`：网页房间结构导出器、灯光模板；保持可点击对象、墙壳和天花分组。
- `assets/source-scripts/`：原始八房间建模脚本及构建工具，供追溯；不保证重新生成后与手工调整模型一致。
- `docs/`：最新状态、开发地图、已知问题、策划案、报告及资产处理记录。
- `archive/lightmap-experiments/`：隔离的旧 Diffuse/AO 实验脚本与报告，非当前资产来源。

请先读 `docs/HANDOFF.md`。网页端无法运行系统托盘、桌面窗口扫描、鼠标穿透和独立桌面猫；这些在另一份 Electron 包中。

历史模型备份已移至 `archive/model-backups/`，不会进入网页构建或 Vercel 部署。当前运行模型仅为 `app/models/` 根目录的八份 `.txt` 与 `rooms.json`。Blender 源文件单个均小于 Git 单文件 100 MiB 限制，可以由 Git 客户端提交；GitHub 网页上传仍受单文件 25 MB 限制。
