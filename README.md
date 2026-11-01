# ai-portfolio

何年的 **AI 作品集**（GitHub Pages）。

- 仓库：https://github.com/luke-arch-git/ai-portfolio
- 站点：https://luke-arch-git.github.io/ai-portfolio/
- 以后所有 AI 相关作品都发到这里。

## 当前作品

| 作品 | 预览 / 链接 |
| --- | --- |
| STARLING-01 · 星际信使 | [/projects/starling-01/preview/](https://luke-arch-git.github.io/ai-portfolio/projects/starling-01/preview/) |
| Sunset Valley | [Pages](https://luke-arch-git.github.io/sunset-valley/) · [仓库](https://github.com/luke-arch-git/sunset-valley) |
| AI Micro Product Radar | [仓库](https://github.com/luke-arch-git/ai-micro-product-radar) |
| MiMo Agent Workflow Lab | [仓库](https://github.com/luke-arch-git/mimo-agent-workflow-lab) |


## 如何新增作品

1. 在 `projects/<slug>/` 放入作品文件（需要网页预览时保留 `preview/`，交付物放 `output/`）。
2. 在 `works.json` 增加一条：`id`、`title`、`date`、`summary`、`hero`、`href`、可选 `tags` / `downloads`。
3. 推送到 `main`。Pages 从 `main` 根目录发布，大约一两分钟后站点更新。

路径一律用相对路径，因为站点挂在 `/ai-portfolio/` 子路径下。

## 媒体约定

- 首页主图建议正方形或接近 1:1，宽度 ≥ 1200px。
- 不要提交：`node_modules/`、`.venv/`、`animation_frames/`、试渲染大目录。
- 单文件尽量 &lt; 50MB；更大的放到网盘并在 `downloads` 里写外链。

## STARLING-01 下载

- [GLB](projects/starling-01/output/STARLING-01.glb)
- [Blender `.blend`](projects/starling-01/output/STARLING-01.blend)
- [10 秒旋转视频](projects/starling-01/output/STARLING-01_Turntable_10s.mp4)
