# 何年 · AI 作品集

何年（He Nian）的 AI 作品长期住处。三维道具、动态影像、代码生成、数学可视化和智能体实验，都从这一个静态站点进去。

以后新的 AI 相关作品，也加到这里。单独的仓库可以继续存在，但应当在根目录的 `works.json` 里有一条，让这个站点当目录。

线上地址：<https://luke-arch-git.github.io/ai-portfolio/>

GitHub Pages 从 `main` 分支的根目录发布。没有构建步骤。

## 现在有什么

| 作品 | 时间 | 在本站 |
| --- | --- | --- |
| [STARLING-01 · 星际信使](projects/starling-01/preview/) | 2026-11 | 首页第一张卡片。实时预览在 `projects/starling-01/preview/`，主视觉、GLB、Blender 工程和 10 秒旋转视频都在 `projects/starling-01/output/`。不要移动或覆盖这个目录。 |
| 新粗野主义动态样片 | 2026-11 | 六张静帧，加 12 秒无声预览。完整母版另存，不进这个仓库。 |
| 日落山谷 | 2026-10 | 卡片直接打开[在线场景](https://luke-arch-git.github.io/sunset-valley/)。封面用原仓库的图片地址，成片和源码也只做链接，不复制进本仓库。 |
| 最短路径 · 蚂蚁配音重制 | 2026 | 只有文字。成片还没公开，所以没有画面，也没有外链。 |
| AI 小产品雷达 | 2026-07 | 卡片链到[仓库](https://github.com/luke-arch-git/ai-micro-product-radar)和[已发布页面](https://luke-arch-git.github.io/ai-micro-product-radar/)，不复制文件。 |
| MiMo 智能体工作流实验 | 2026-04 | 卡片链到[仓库](https://github.com/luke-arch-git/mimo-agent-workflow-lab)，不复制文件。 |

### STARLING-01 下载

这些路径是站点在用的，保持不动：

- 主视觉：`projects/starling-01/output/STARLING-01_Hero_2048.png`
- 实时预览：`projects/starling-01/preview/`
- [GLB](projects/starling-01/output/STARLING-01.glb)（11.9 MB）
- [Blender `.blend`](projects/starling-01/output/STARLING-01.blend)（7.3 MB）
- [10 秒旋转视频](projects/starling-01/output/STARLING-01_Turntable_10s.mp4)（768² · 10s）

## 本地预览

不要双击 HTML。浏览器不允许页面去读旁边的 `works.json`。在仓库根目录开一个静态服务器：

```bash
python3 -m http.server 8080
```

然后打开 <http://localhost:8080/>。

正式站点挂在 `/ai-portfolio/` 下面。链接和媒体都用相对路径，所以本地根目录和 GitHub Pages 子路径都能打开。如果要按正式路径看一遍：

```bash
cd /tmp
ln -s /你的路径/ai-portfolio ai-portfolio
python3 -m http.server 8080
```

打开 <http://localhost:8080/ai-portfolio/>。

STARLING 的实时预览同样是静态文件。从首页卡片进去即可，不必单独装依赖。`projects/starling-01/preview/` 里的 `node_modules` 没有提交，也不需要。

## 如何新增一件作品 {#add-a-work}

1. 定一个 id，只用小写英文、数字和连字符，例如 `math-garden`。详情地址是 `work.html?id=math-garden`。改了 id，旧链接就失效。
2. 把文件放进仓库。两条路，选一条：
   - 作品自己就是一个目录：`projects/math-garden/`，预览页放 `preview/`，交付物放 `output/`。STARLING-01 就是这样。
   - 只在这个站点上放预览：图片或短视频放进 `media/math-garden/`。
3. 打开根目录的 `works.json`，在数组**最前面**加一条。数组顺序就是站上的编号。首页第一件作品会做成大卡片，所以新作品如果要顶到最前，就放在 STARLING 之前；想让 STARLING 继续排第一，就插在它后面。
4. 至少写上 `id`、`date`、`tags`、`title`、`summary`。有主视觉就写 `hero` 和 `href`。有文件可下就写 `downloads`。站内图文用 `media` 和 `description`。
5. 用本地服务器看首页、作品列表和详情。中文、英文都点一次。
6. 提交并推到 `main`。Pages 会自己更新，通常一两分钟。

不用改 HTML，也不用运行打包命令。

`works.json` 是一个数组，不是包在 `{ "works": [] }` 里。第一条目前必须仍是 STARLING-01，除非有意调整顺序。它的 `hero`、`href`、`downloads` 不要改路径。

照着改的例子：

```json
{
  "id": "math-garden",
  "title": { "zh": "数学花园", "en": "Math Garden" },
  "date": "2026-12",
  "tags": ["education", "generative"],
  "summary": { "zh": "一句话说明这件作品是什么。", "en": "One sentence on what this is." },
  "description": {
    "zh": ["第一段。", "第二段。"],
    "en": ["First paragraph.", "Second paragraph."]
  },
  "note": {
    "zh": "需要读者先知道的限制。没有就删掉这个字段。",
    "en": "A limit the reader should know. Delete this field if there is nothing to flag."
  },
  "media": [
    {
      "type": "video",
      "src": "media/math-garden/preview.mp4",
      "poster": "media/math-garden/cover.jpg",
      "width": 1280,
      "height": 720,
      "caption": { "zh": "预览里实际有什么。", "en": "What the preview actually shows." }
    },
    {
      "type": "image",
      "src": "media/math-garden/cover.jpg",
      "width": 1600,
      "height": 900,
      "alt": { "zh": "画面里看得见的东西。", "en": "What is visible in the picture." },
      "caption": { "zh": "封面", "en": "Cover" }
    }
  ],
  "links": [
    {
      "label": { "zh": "仓库", "en": "Repository" },
      "href": "https://github.com/luke-arch-git/math-garden"
    }
  ]
}
```

如果作品像 STARLING 一样自带预览页和可下载文件，用这一形：

```json
{
  "id": "starling-01",
  "title": "STARLING-01",
  "subtitle": "星际信使",
  "date": "2026-11",
  "tags": ["3d", "generative", "realtime"],
  "summary": "一句话。",
  "hero": "projects/starling-01/output/STARLING-01_Hero_2048.png",
  "href": "projects/starling-01/preview/",
  "downloads": [
    {"label": "GLB 模型", "href": "projects/starling-01/output/STARLING-01.glb", "note": "11.9 MB"}
  ]
}
```

JSON 不支持注释。多写或少写逗号，整站作品都会读不出来。改完可以确认文件没坏：

```bash
python3 -c "import json; json.load(open('works.json'))"
```

## 字段

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `id` | 是 | 小写 slug。详情地址用它，不要用中文或空格。 |
| `date` | 是 | `2026`、`2026-11` 或 `2026-11-02`。页面按原文显示。 |
| `tags` | 是 | 数组。见下一节。一件作品可以有多个。 |
| `title` | 是 | 字符串，或 `{ "zh", "en" }`。专名可以直接写字符串，例如 `STARLING-01`。 |
| `subtitle` | 否 | 标题下面的一行，例如 `星际信使`。 |
| `summary` | 是 | 卡片上的短说明。字符串，或 `{ "zh", "en" }`。英文界面若要另一句，可另写 `summaryEn`。 |
| `description` | 建议 | `{ "zh": ["段"], "en": ["..."] }`。详情页正文。 |
| `note` | 否 | 一条需要先看见的限制，例如「站内只是预览」或「成片未公开」。 |
| `hero` | 否 | 主视觉。站内用相对路径，例如 STARLING 的 `projects/starling-01/output/STARLING-01_Hero_2048.png`。外链作品可以用原站的 `https://` 图片地址，不要把大文件复制进来。留空就显示文字卡片。 |
| `href` | 否 | 卡片主链接。STARLING 指向 `projects/starling-01/preview/`。日落山谷、雷达和 MiMo 实验指向各自的 Pages 或仓库。不写就进详情页。 |
| `downloads` | 否 | `{ "label", "href", "note" }` 的数组。同站文件会带下载。 |
| `media` | 否 | 视频和图片，给没有 `hero` 的作品，或详情页的补充静帧。没有就省略或写 `[]`。 |
| `links` | 否 | 详情页上的外链。只写真实地址。不要放打不开的占位链接。 |
| `role` | 否 | 不写是正常作品，出现在首页主体。`"repository"` 放在首页「其他公开仓库」，不要求配图。 |

有 `hero` 时，卡片和首页大图用它。没有 `hero` 时，用 `media` 里的第一张图。第一件非仓库作品会做成首页大卡片。

详情页地址是 `work.html?id=作品id`。这是静态站点，没有为每件作品单独生成 HTML。

## 标签

筛选只用这些词。中英对照由站点处理，JSON 里写 id。

| id | 中文 | 什么时候用 |
| --- | --- | --- |
| `3d` | 三维 | 模型、道具、可旋转的物体 |
| `realtime` | 实时 | 浏览器里能直接转、能直接看 |
| `motion` | 动态 | 影像、动效、样片 |
| `generative` | 生成 | 程序生成的图像、场景、声音 |
| `education` | 教育 | 把知识做成可以学的材料 |
| `agent` | 智能体 | 智能体、工作流、自动流程 |
| `experiment` | 实验 | 还在试、规模不大的公开实验 |
| `web` | 网页 | 浏览器里直接打开的场景或页面 |
| `research` | 研究 | 方法、信号和资料整理 |
| `product` | 产品 | 对着真实使用场景做的小产品 |

写了表以外的标签，站点仍会显示原文。请尽量用这些，筛选才整齐。

## 媒体

路径相对于仓库根目录：

```text
media/math-garden/cover.jpg
projects/starling-01/output/STARLING-01_Hero_2048.png
```

不要写成 `/media/...`，也不要写成 `/ai-portfolio/media/...`。前一种在 GitHub Pages 上会跑到用户主页的根上去，后一种在本地根目录预览时会找不到。

文件名用小写英文和连字符。已有的 STARLING 文件名保持原样，不要为了这条规则去改名。

图片：

- JPG、PNG 或 WebP。
- 新图长边不超过 2048，单张尽量小于 500KB。首页卡片裁成方图，重要内容放在画面中间。
- 每张 `media` 图都写 `width`、`height`，以及中英 `alt`。`alt` 描述画面里看得见的东西。
- 竖图可以，详情页按原比例显示。

视频：

- MP4，H.264。有声音再加 AAC。
- 这个仓库只放预览。建议 30 秒以内、1080p 或更低，尽量小于 15MB。
- 完整母版、工程缓存和未压缩成片不要推进来。STARLING 的 blend / glb 是交付物，已经在 `projects/starling-01/output/`，不要再复制一份到 `media/`。
- 写上 `poster`、`width`、`height`，并用 `caption` 说明这段预览实际覆盖了什么、有没有声音。

没有媒体就不要造一张假图。像「最短路径 · 蚂蚁配音重制」那样，不写 `hero` 和 `media`，用 `note` 说明为什么没有画面。

## 双语

中文是默认语言。右上角可以切到英文，选择记在这台浏览器里。

面向读者的句子可以写成 `{ "zh": "...", "en": "..." }`。英文缺了会回退到中文，所以中文一定要有。专名和已经写好的中文 `summary` 可以保持字符串。

界面上的「作品 / 关于 / 筛选」在 `site.js` 的 `DICT` 里。一般加作品不用改那个文件。

## 路径和发布

- 页面在仓库根目录：`index.html`、`works.html`、`work.html`、`about.html`、`404.html`。
- 样式是 `site.css`，行为是 `site.js`，数据是 `works.json`。
- `projects/starling-01/` 是完整交付，站点只引用它。改作品列表时不要重写这个目录里的预览、脚本或输出文件。
- 根目录的 `.nojekyll` 让 GitHub Pages 按原样发布文件，不要删。
- 字体用系统里的中文宋黑，不从外部字体站加载。
- `.gitignore` 会挡住 `node_modules/`、`.venv/`、`animation_frames/`。不要把这些推进来。
- 推到 `main` 即发布到 <https://luke-arch-git.github.io/ai-portfolio/>。

## 作品以后放哪里

这个仓库是目录，不是临时展览。

- 新的 AI 作品：在 `works.json` 加一条。预览媒体放 `media/<id>/`，或者自成 `projects/<id>/`。
- 已经有独立仓库的项目：仓库留在原地，这里加一条 `role` 为 `"repository"` 的卡片，链过去。
- 还不能公开的成片：可以先写条目和说明，先不放 `media`、`hero`、`links`。不要放一个打不开的假地址。

## 许可

`media/` 和 `projects/` 里的画面、模型和预览是作品本身，版权归作者。页面结构（HTML、CSS、JS）可以拿去改成自己的作品集。
