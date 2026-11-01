/* Renders the portfolio from data/works.json. No build step. */
(function () {
  var KNOWN_TAGS = ["3d", "realtime", "motion", "generative", "education", "agent", "experiment"];
  var TAG_LABELS = {
    "3d": { zh: "三维", en: "3D" },
    realtime: { zh: "实时", en: "Realtime" },
    motion: { zh: "动态", en: "Motion" },
    generative: { zh: "生成", en: "Generative" },
    education: { zh: "教育", en: "Education" },
    agent: { zh: "智能体", en: "Agent" },
    experiment: { zh: "实验", en: "Experiment" }
  };

  var DICT = {
    zh: {
      skip: "跳到内容",
      navLabel: "页面",
      navWorks: "作品",
      navAbout: "关于",
      langLabel: "语言",
      heroLede: "把复杂的东西，做成可以学习的形状。",
      heroDek: "从地理信息走到人工智能应用。关心编程、AI 教育、数学可视化，以及让难的知识变得可学。",
      footerBlurb: "以后的 AI 作品也放在这里。",
      loading: "正在读取作品…",
      loadError: "作品数据没有读出来。请确认 works.json 可以访问。如果是直接双击打开的文件，请改用本地服务器。",
      openPreview: "进入预览",
      dossier: "说明",
      downloadsHeading: "下载",
      worksTitle: "作品",
      worksDek: "按标签看。一件作品可以同时属于好几类。新作品写进数据文件就会出现在这里。",
      filtersLabel: "按标签筛选",
      filterAll: "全部",
      empty: "这个标签下还没有作品。",
      notFoundTitle: "没有找到这件作品",
      notFoundBody: "链接可能过期了。作品列表里可以重新选。",
      backToWorks: "全部作品",
      linksHeading: "链接",
      stillsHeading: "静帧",
      plateEmpty: "暂无画面",
      plateRepo: "仓库",
      newWindow: "新窗口",
      close: "关闭",
      prev: "上一张",
      next: "下一张",
      lightbox: "静帧",
      lbHint: "左右方向键可以切换",
      leadCta: "静帧与说明",
      previewKicker: "预览",
      moreWorks: "更多作品",
      moreWorksDek: "同样收在这个站点里。",
      repoTitle: "其他公开仓库",
      repoDek: "只链出去，不放替代截图。",
      view: "查看",
      aboutTitle: "关于",
      aboutP1: "何年（He Nian）。GitHub 账号是 luke-arch-git。",
      aboutP2: "路径从地理信息系统走到人工智能应用。想做的事很具体：用程序和图像，把复杂的知识变成可以看见、可以跟着学的形状。",
      aboutP3: "这个网站是这些作品的长期住处。新的 AI 相关作品也收在这里。",
      aboutP4: "添加一件作品，改仓库根目录的 works.json。画面可以放进 media/，也可以像 STARLING-01 一样放在 projects/ 里再链过来。",
      readmeLink: "添加步骤",
      interestsLabel: "关心",
      int1: "人工智能",
      int2: "编程",
      int3: "AI 教育",
      int4: "数学可视化",
      int5: "让复杂的知识变得可学",
      missingTitle: "这个页面不在",
      missingBody: "地址可能写错了。",
      homeLink: "回首页",
      home: "首页",
      nameShort: "何年",
      countAll: "共 {n} 件",
      countSome: "{shown} / {total} 件",
      stripLabel: "样片静帧"
    },
    en: {
      skip: "Skip to content",
      navLabel: "Pages",
      navWorks: "Works",
      navAbout: "About",
      langLabel: "Language",
      heroLede: "Give complex ideas a shape someone can learn from.",
      heroDek: "From GIS into applied AI. Interested in programming, AI education, math visualization, and making difficult knowledge learnable.",
      footerBlurb: "Future AI work belongs here too.",
      loading: "Loading works…",
      loadError: "The works file could not be read. Check that works.json is available. Opening the HTML file directly will not work; use a local server.",
      openPreview: "Open preview",
      dossier: "Notes",
      downloadsHeading: "Downloads",
      worksTitle: "Works",
      worksDek: "Filter by tag. A work can sit in more than one. New pieces show up here once they are in the data file.",
      filtersLabel: "Filter by tag",
      filterAll: "All",
      empty: "Nothing under this tag yet.",
      notFoundTitle: "This work is not on the site",
      notFoundBody: "The link may be out of date. The index lists everything that is here.",
      backToWorks: "All works",
      linksHeading: "Links",
      stillsHeading: "Stills",
      plateEmpty: "No picture yet",
      plateRepo: "Repo",
      newWindow: "new window",
      close: "Close",
      prev: "Previous",
      next: "Next",
      lightbox: "Still",
      lbHint: "Arrow keys move between stills",
      leadCta: "Stills and notes",
      previewKicker: "Preview",
      moreWorks: "More works",
      moreWorksDek: "Also kept on this site.",
      repoTitle: "Other public repositories",
      repoDek: "Links only. No stand-in screenshots.",
      view: "View",
      aboutTitle: "About",
      aboutP1: "He Nian (何年). GitHub: luke-arch-git.",
      aboutP2: "The path runs from geographic information systems into applied AI. The aim is concrete: use programming and images to make complex knowledge visible and learnable.",
      aboutP3: "This site is the long-term home for that work. New AI pieces belong here.",
      aboutP4: "Adding a work means editing works.json at the repository root. Media can live in media/, or in projects/ with a link, the way STARLING-01 does.",
      readmeLink: "How to add a work",
      interestsLabel: "Interests",
      int1: "AI",
      int2: "Programming",
      int3: "AI education",
      int4: "Math visualization",
      int5: "Making complex knowledge learnable",
      missingTitle: "This page is not here",
      missingBody: "The address may be wrong.",
      homeLink: "Back home",
      home: "Home",
      nameShort: "He Nian",
      countAll: "{n} works",
      countSome: "{shown} of {total}",
      stripLabel: "Showreel stills"
    }
  };

  var state = {
    lang: "zh",
    works: [],
    filter: "all",
    ready: false,
    error: false
  };
  var gallery = [];
  var galleryIndex = 0;

  function t(key) {
    var pack = DICT[state.lang] || DICT.zh;
    if (pack[key] != null) return pack[key];
    return DICT.zh[key] != null ? DICT.zh[key] : key;
  }

  function tx(value) {
    if (!value) return "";
    if (typeof value === "string") return value;
    return value[state.lang] || value.zh || value.en || "";
  }

  function titleOf(work) {
    if (work.title && typeof work.title === "object") return tx(work.title);
    if (state.lang === "en" && work.titleEn) return work.titleEn;
    return work.title || "";
  }

  function summaryOf(work) {
    if (state.lang === "en" && typeof work.summaryEn === "string") return work.summaryEn;
    return tx(work.summary);
  }

  function tagLabel(tag) {
    var row = TAG_LABELS[tag];
    if (!row) return tag;
    return row[state.lang] || row.zh || tag;
  }

  function h(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        var value = attrs[key];
        if (value == null || value === false) return;
        if (key === "class") node.className = value;
        else if (key === "text") node.textContent = String(value);
        else node.setAttribute(key, value === true ? "" : String(value));
      });
    }
    if (children != null) {
      var list = Array.isArray(children) ? children : [children];
      list.forEach(function (child) {
        if (child == null || child === false) return;
        node.append(child.nodeType ? child : document.createTextNode(String(child)));
      });
    }
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function safeUrl(href) {
    if (typeof href !== "string") return "";
    var value = href.trim();
    if (!value) return "";
    try {
      var url = new URL(value, window.location.href);
      if (url.protocol === "http:" || url.protocol === "https:") return value;
    } catch (error) {
      return "";
    }
    return "";
  }

  function isExternal(href) {
    try {
      return new URL(href, window.location.href).origin !== window.location.origin;
    } catch (error) {
      return false;
    }
  }

  function workHref(work) {
    return "work.html?id=" + encodeURIComponent(work.id);
  }

  function workNo(work) {
    var index = state.works.findIndex(function (item) { return item.id === work.id; });
    return String(index < 0 ? 0 : index + 1).padStart(2, "0");
  }

  function makeLink(href, label, className) {
    var safe = safeUrl(href);
    if (!safe) return null;
    var anchor = h("a", { class: className || "btn", href: safe });
    anchor.append(document.createTextNode(label));
    if (isExternal(safe)) {
      anchor.target = "_blank";
      anchor.rel = "noopener noreferrer";
      anchor.append(h("span", { class: "visually-hidden", text: "（" + t("newWindow") + "）" }));
      anchor.append(document.createTextNode(" ↗"));
    }
    return anchor;
  }

  function makeImage(media, eager) {
    var src = safeUrl(media.src);
    if (!src) return null;
    return h("img", {
      src: src,
      alt: tx(media.alt) || "",
      width: media.width || null,
      height: media.height || null,
      loading: eager ? "eager" : "lazy",
      decoding: "async"
    });
  }

  function makePlayer(media, poster) {
    var src = safeUrl(media.src);
    if (!src) return null;
    var figure = h("figure", { class: "player" });
    var video = document.createElement("video");
    video.controls = true;
    video.playsInline = true;
    video.setAttribute("playsinline", "");
    video.preload = "metadata";
    if (media.width) video.width = media.width;
    if (media.height) video.height = media.height;
    var posterUrl = safeUrl(poster || media.poster || "");
    if (posterUrl) video.poster = posterUrl;
    var source = document.createElement("source");
    source.src = src;
    source.type = media.mime || "video/mp4";
    video.append(source);
    figure.append(video);
    var caption = tx(media.caption);
    if (caption) figure.append(h("figcaption", { text: caption }));
    return figure;
  }

  function tagList(work) {
    var list = h("ul", { class: "tags" });
    (work.tags || []).forEach(function (tag) {
      list.append(h("li", { class: "tag", text: tagLabel(tag) }));
    });
    return list;
  }

  function videoOf(work) {
    return (work.media || []).find(function (item) { return item.type === "video"; });
  }

  function imagesOf(work) {
    return (work.media || []).filter(function (item) { return item.type === "image" && safeUrl(item.src); });
  }

  function isPiece(work) {
    return work.role !== "repository";
  }

  function primaryDest(work) {
    if (work.href && safeUrl(work.href)) return work.href;
    return workHref(work);
  }

  function coverOf(work) {
    if (work.hero && safeUrl(work.hero)) {
      var alt = work.heroAlt ? tx(work.heroAlt) : (titleOf(work) + (work.subtitle ? " " + work.subtitle : ""));
      return {
        src: work.hero,
        alt: alt,
        width: work.heroWidth || null,
        height: work.heroHeight || null
      };
    }
    var image = imagesOf(work)[0];
    if (!image) return null;
    return {
      src: image.src,
      alt: tx(image.alt),
      width: image.width || null,
      height: image.height || null,
      portrait: image.height && image.width && Number(image.height) > Number(image.width)
    };
  }

  function makeDownload(item) {
    var safe = safeUrl(item.href);
    if (!safe) return null;
    var anchor = h("a", { class: "dl", href: safe });
    anchor.append(h("span", { text: downloadLabel(item) }));
    anchor.append(h("b", { text: item.note || "↘" }));
    if (!isExternal(safe)) anchor.setAttribute("download", "");
    else {
      anchor.target = "_blank";
      anchor.rel = "noopener noreferrer";
    }
    return anchor;
  }

  function downloadLabel(item) {
    if (state.lang === "en" && item.labelEn) return item.labelEn;
    if (item.label && typeof item.label === "object") return tx(item.label);
    return item.label || "";
  }

  function appendDownloads(parent, work) {
    var items = (work.downloads || []).map(makeDownload).filter(Boolean);
    if (!items.length) return;
    var list = h("div", { class: "downloads" });
    items.forEach(function (anchor) { list.append(anchor); });
    parent.append(list);
  }

  function fillHeading(node, work) {
    node.append(document.createTextNode(titleOf(work)));
    if (work.subtitle) node.append(h("span", { text: work.subtitle }));
  }

  function captureVideo() {
    var video = document.querySelector("main video");
    if (!video) return null;
    var source = video.querySelector("source");
    return {
      src: source ? source.getAttribute("src") : "",
      time: video.currentTime || 0,
      paused: video.paused
    };
  }

  function restoreVideo(saved) {
    if (!saved || !saved.time) return;
    var video = document.querySelector("main video");
    if (!video) return;
    var source = video.querySelector("source");
    var src = source ? source.getAttribute("src") : "";
    if (saved.src && src && saved.src !== src) return;
    var apply = function () {
      try { video.currentTime = saved.time; } catch (error) { /* ignore */ }
      if (!saved.paused) video.play().catch(function () {});
    };
    if (video.readyState >= 1) apply();
    else video.addEventListener("loadedmetadata", apply, { once: true });
  }

  function renderStrip(work, images) {
    var scroller = h("ul", { class: "strip", tabindex: "0", "aria-label": t("stripLabel") });
    images.forEach(function (image, index) {
      var picture = makeImage(image, index === 0);
      if (!picture) return;
      var anchor = h("a", { href: workHref(work) + "#stills" }, picture);
      scroller.append(h("li", null, anchor));
    });
    return scroller;
  }

  function renderLead(work) {
    var section = h("section", { class: "block lead", "aria-labelledby": "lead-title" });
    var grid = h("div", { class: "lead-grid" });
    var cover = coverOf(work);
    var video = videoOf(work);
    var images = imagesOf(work);
    if (cover && (work.hero || !video)) {
      var figureLink = h("a", {
        class: "lead-figure",
        href: primaryDest(work),
        "aria-label": (state.lang === "en" ? "Open " : "打开 ") + titleOf(work)
      });
      figureLink.append(h("img", {
        src: safeUrl(cover.src),
        alt: cover.alt || "",
        width: cover.width || null,
        height: cover.height || null
      }));
      grid.append(figureLink);
    } else if (video) {
      var player = makePlayer(video, (video && video.poster) || (images[0] && images[0].src) || "");
      if (player) grid.append(player);
    }
    var copy = h("div", { class: "lead-copy" });
    var kicker = h("p", { class: "card-kicker" });
    kicker.append(h("span", { class: "idx", text: workNo(work) }));
    kicker.append(document.createTextNode(" · "));
    kicker.append(h("time", { datetime: work.date || "", text: work.date || "" }));
    copy.append(kicker);
    var heading = h("h2", { id: "lead-title" });
    fillHeading(heading, work);
    copy.append(heading);
    copy.append(h("p", { class: "lead-summary", text: summaryOf(work) }));
    copy.append(tagList(work));
    if (tx(work.note)) copy.append(h("p", { class: "note", text: tx(work.note) }));
    var actions = h("div", { class: "hero-actions" });
    var cta = makeLink(primaryDest(work), work.href ? t("openPreview") : t("leadCta"), "btn");
    if (cta) actions.append(cta);
    if (work.href) {
      var dossier = makeLink(workHref(work), t("dossier"), "btn btn-quiet");
      if (dossier) actions.append(dossier);
    }
    if (actions.childNodes.length) copy.append(actions);
    appendDownloads(copy, work);
    grid.append(copy);
    section.append(grid);
    if (!work.hero && images.length) section.append(renderStrip(work, images));
    return section;
  }

  function renderCard(work) {
    var item = h("li");
    var article = h("article", { class: "card" });
    var dest = primaryDest(work);
    var mediaLink = h("a", {
      class: "card-media",
      href: dest,
      "aria-label": (state.lang === "en" ? "Open " : "打开 ") + titleOf(work)
    });
    var cover = coverOf(work);
    if (cover) {
      if (cover.portrait) mediaLink.classList.add("portrait");
      mediaLink.append(h("img", {
        src: safeUrl(cover.src),
        alt: cover.alt || "",
        width: cover.width || null,
        height: cover.height || null,
        loading: "lazy",
        decoding: "async"
      }));
    } else {
      var plate = h("div", { class: "plate" });
      plate.append(h("strong", { text: work.role === "repository" ? t("plateRepo") : t("plateEmpty") }));
      plate.append(h("span", { class: "idx", text: workNo(work) }));
      mediaLink.append(plate);
    }
    var body = h("div", { class: "card-body" });
    var kicker = h("p", { class: "card-kicker" });
    kicker.append(h("span", { class: "idx", text: workNo(work) }));
    kicker.append(document.createTextNode(" · "));
    kicker.append(h("time", { datetime: work.date || "", text: work.date || "" }));
    var title = h("h3");
    var titleLink = h("a", { href: dest });
    fillHeading(titleLink, work);
    title.append(titleLink);
    body.append(kicker, title, h("p", { class: "card-summary", text: summaryOf(work) }), tagList(work));
    if (work.href) {
      var dossier = h("a", { class: "card-more", href: workHref(work), text: t("dossier") });
      body.append(dossier);
    }
    article.append(mediaLink, body);
    appendDownloads(article, work);
    item.append(article);
    return item;
  }

  function renderMosaic(works) {
    var section = h("section", { class: "block", "aria-labelledby": "more-title" });
    var head = h("div", { class: "section-head" });
    head.append(h("h2", { id: "more-title", text: t("moreWorks") }));
    head.append(h("p", { text: t("moreWorksDek") }));
    var list = h("ul", { class: "mosaic" });
    works.forEach(function (work) { list.append(renderCard(work)); });
    section.append(head, list);
    return section;
  }

  function renderRepos(works) {
    var section = h("section", { class: "block", "aria-labelledby": "repo-title" });
    var head = h("div", { class: "section-head" });
    head.append(h("h2", { id: "repo-title", text: t("repoTitle") }));
    head.append(h("p", { text: t("repoDek") }));
    var list = h("ul", { class: "repo-list" });
    works.forEach(function (work) {
      var row = h("a", { class: "repo-row", href: workHref(work) });
      row.append(h("span", { class: "idx", text: workNo(work) }));
      var copy = h("span", { class: "repo-copy" });
      copy.append(h("h3", { class: "repo-title", text: titleOf(work) }));
      copy.append(h("span", { class: "repo-summary", text: summaryOf(work) }));
      var tags = (work.tags || []).map(tagLabel).join(" · ");
      if (tags) copy.append(h("span", { class: "repo-tags", text: tags }));
      row.append(copy);
      row.append(h("span", { class: "go", text: t("view") + " →" }));
      list.append(h("li", null, row));
    });
    section.append(head, list);
    return section;
  }

  function renderHome() {
    var root = document.getElementById("home-dynamic");
    if (!root) return;
    var saved = captureVideo();
    clear(root);
    var pieces = state.works.filter(isPiece);
    var repos = state.works.filter(function (work) { return work.role === "repository"; });
    var lead = pieces[0] || null;
    var rest = pieces.slice(1);
    if (lead) root.append(renderLead(lead));
    if (rest.length) root.append(renderMosaic(rest));
    if (repos.length) root.append(renderRepos(repos));
    restoreVideo(saved);
  }

  function tagAllowed(tag) {
    if (tag === "all") return true;
    if (Object.prototype.hasOwnProperty.call(TAG_LABELS, tag)) return true;
    return state.works.some(function (work) { return (work.tags || []).indexOf(tag) !== -1; });
  }

  function activeTags() {
    var present = {};
    state.works.forEach(function (work) {
      (work.tags || []).forEach(function (tag) { present[tag] = true; });
    });
    var ordered = KNOWN_TAGS.filter(function (tag) { return present[tag]; });
    Object.keys(present).forEach(function (tag) {
      if (ordered.indexOf(tag) === -1) ordered.push(tag);
    });
    return ordered;
  }

  function countText(shown, total) {
    var template = shown === total ? t("countAll") : t("countSome");
    return template.replace("{n}", total).replace("{shown}", shown).replace("{total}", total);
  }

  function buildFilters() {
    var group = document.getElementById("filters");
    if (!group) return;
    var tags = ["all"].concat(activeTags());
    clear(group);
    tags.forEach(function (tag) {
      var count = tag === "all"
        ? state.works.length
        : state.works.filter(function (work) { return (work.tags || []).indexOf(tag) !== -1; }).length;
      var checked = state.filter === tag;
      var button = h("button", {
        type: "button",
        class: "filter-btn",
        role: "radio",
        "aria-checked": checked ? "true" : "false",
        tabindex: checked ? "0" : "-1",
        "data-tag": tag,
        "data-focuskey": "filter-" + tag
      });
      var label = tag === "all" ? t("filterAll") : tagLabel(tag);
      button.append(document.createTextNode(label + " " + count));
      group.append(button);
    });
  }

  function renderWorks() {
    var grid = document.getElementById("works-grid");
    if (!grid) return;
    buildFilters();
    var shown = state.works.filter(function (work) {
      return state.filter === "all" || (work.tags || []).indexOf(state.filter) !== -1;
    });
    var count = document.getElementById("works-count");
    if (count) count.textContent = countText(shown.length, state.works.length);
    clear(grid);
    var empty = document.getElementById("empty");
    if (empty) {
      empty.hidden = shown.length > 0;
      empty.textContent = shown.length ? "" : t("empty");
    }
    shown.forEach(function (work) { grid.append(renderCard(work)); });
  }

  function paragraphs(value) {
    var text = value && (value[state.lang] || value.zh || value.en);
    var list = Array.isArray(text) ? text : (text ? [text] : []);
    return list.filter(Boolean).map(function (para) {
      return h("p", { class: "body-copy", text: para });
    });
  }

  function renderGallery(images) {
    gallery = images.map(function (image) {
      return {
        src: safeUrl(image.src),
        alt: tx(image.alt),
        caption: tx(image.caption) || tx(image.alt),
        width: image.width,
        height: image.height,
        portrait: image.height && image.width && Number(image.height) > Number(image.width)
      };
    }).filter(function (item) { return item.src; });

    if (!gallery.length) return null;
    var section = h("section", { class: "work-gallery", id: "stills", "aria-labelledby": "stills-title" });
    section.append(h("h2", { id: "stills-title", text: t("stillsHeading") }));
    var grid = h("div", { class: "gallery" });
    gallery.forEach(function (item, index) {
      var button = h("button", {
        type: "button",
        class: item.portrait ? "shot portrait" : "shot",
        "data-focuskey": "shot-" + index
      });
      button.append(h("img", {
        src: item.src,
        alt: item.alt || "",
        width: item.width || null,
        height: item.height || null,
        loading: index === 0 ? "eager" : "lazy",
        decoding: "async"
      }));
      if (item.caption) button.append(h("span", { class: "shot-cap", text: item.caption }));
      button.addEventListener("click", function () { openLightbox(index); });
      grid.append(button);
    });
    section.append(grid);
    return section;
  }

  function renderWork() {
    var article = document.getElementById("work");
    if (!article) return;
    var saved = captureVideo();
    var dialog = document.getElementById("lightbox");
    var wasOpen = Boolean(dialog && dialog.open);
    var keepIndex = galleryIndex;
    var id = new URLSearchParams(window.location.search).get("id");
    var work = state.works.find(function (item) { return item.id === id; });
    clear(article);
    article.hidden = false;
    gallery = [];

    if (!work) {
      document.title = t("notFoundTitle") + " · " + t("nameShort");
      var missing = h("div", { class: "missing" });
      missing.append(h("h1", { text: t("notFoundTitle") }));
      missing.append(h("p", { text: t("notFoundBody") }));
      var back = makeLink("works.html", t("backToWorks"), "btn");
      if (back) missing.append(back);
      article.append(missing);
      if (wasOpen && dialog) dialog.close();
      return;
    }

    document.title = titleOf(work) + " · " + t("nameShort");
    var head = h("header", { class: "work-head" });
    var kicker = h("p", { class: "card-kicker" });
    kicker.append(h("span", { class: "idx", text: workNo(work) }));
    kicker.append(document.createTextNode(" · "));
    kicker.append(h("time", { datetime: work.date || "", text: work.date || "" }));
    head.append(kicker);
    var heading = h("h1", { class: "work-title" });
    fillHeading(heading, work);
    head.append(heading);
    if (work.title && typeof work.title === "object") {
      var otherLang = state.lang === "zh" ? "en" : "zh";
      if (work.title[otherLang] && work.title[otherLang] !== titleOf(work)) {
        head.append(h("p", { class: "work-alt", lang: otherLang, text: work.title[otherLang] }));
      }
    }
    head.append(tagList(work));
    if (summaryOf(work)) head.append(h("p", { class: "work-summary", text: summaryOf(work) }));
    article.append(head);
    if (tx(work.note)) article.append(h("p", { class: "note", text: tx(work.note) }));

    var video = videoOf(work);
    var images = imagesOf(work);
    if (work.hero) {
      var heroCover = coverOf(work);
      if (heroCover) {
        var heroFigure = h("figure", { class: "player" });
        heroFigure.append(h("img", {
          src: safeUrl(heroCover.src),
          alt: heroCover.alt || "",
          width: heroCover.width || null,
          height: heroCover.height || null
        }));
        article.append(heroFigure);
      }
    } else if (video) {
      var player = makePlayer(video, (video && video.poster) || (images[0] && images[0].src) || "");
      if (player) article.append(player);
    }

    var copy = h("div", { class: "work-copy" });
    paragraphs(work.description).forEach(function (para) { copy.append(para); });
    var links = [];
    if (work.href && safeUrl(work.href)) {
      var previewLink = makeLink(work.href, t("openPreview"), "btn");
      if (previewLink) links.push(previewLink);
    }
    (work.links || []).forEach(function (link) {
      var anchor = makeLink(link.href, tx(link.label) || link.href, "btn");
      if (anchor) links.push(anchor);
    });
    var downloads = (work.downloads || []).map(makeDownload).filter(Boolean);
    var hasAside = links.length || downloads.length;
    var grid = h("div", { class: hasAside ? "work-grid has-aside" : "work-grid" });
    grid.append(copy);
    if (hasAside) {
      var aside = h("aside", { class: "work-aside" });
      if (links.length) {
        aside.append(h("h2", { class: "aside-title", text: t("linksHeading") }));
        var list = h("div", { class: "link-list" });
        links.forEach(function (link) { list.append(link); });
        aside.append(list);
      }
      if (downloads.length) {
        aside.append(h("h2", { class: "aside-title downloads-title", text: t("downloadsHeading") }));
        var dlist = h("div", { class: "downloads" });
        downloads.forEach(function (anchor) { dlist.append(anchor); });
        aside.append(dlist);
      }
      grid.append(aside);
    }
    if (copy.childNodes.length || hasAside) article.append(grid);

    var gallerySection = renderGallery(images);
    if (gallerySection) article.append(gallerySection);
    restoreVideo(saved);
    if (wasOpen && gallery.length) openLightbox(Math.min(keepIndex, gallery.length - 1));
    else if (wasOpen && dialog) dialog.close();
  }

  function openLightbox(index) {
    var dialog = document.getElementById("lightbox");
    if (!dialog || !gallery.length) return;
    galleryIndex = (index + gallery.length) % gallery.length;
    var item = gallery[galleryIndex];
    var image = document.getElementById("lb-img");
    image.src = item.src;
    image.alt = item.alt || "";
    if (item.width) image.width = item.width;
    if (item.height) image.height = item.height;
    document.getElementById("lb-cap").textContent = item.caption || "";
    document.getElementById("lb-count").textContent = (galleryIndex + 1) + " / " + gallery.length;
    var multi = gallery.length > 1;
    document.getElementById("lb-prev").hidden = !multi;
    document.getElementById("lb-next").hidden = !multi;
    var hint = document.getElementById("lb-hint");
    if (hint) hint.hidden = !multi;
    dialog.setAttribute("aria-label", item.caption || t("lightbox"));
    if (!dialog.open) dialog.showModal();
  }

  function stepLightbox(delta) {
    if (gallery.length < 2) return;
    openLightbox(galleryIndex + delta);
  }

  function focusedKey() {
    var el = document.activeElement;
    return el && el.dataset ? (el.dataset.focuskey || "") : "";
  }

  function restoreFocus(key) {
    if (!key || !window.CSS || !CSS.escape) return;
    var el = document.querySelector('[data-focuskey="' + CSS.escape(key) + '"]');
    if (el) el.focus();
  }

  function render() {
    var key = focusedKey();
    var page = document.body.dataset.page;
    if (page === "home") renderHome();
    else if (page === "works") renderWorks();
    else if (page === "work") renderWork();
    restoreFocus(key);
  }

  function renderStatus() {
    var el = document.getElementById("status");
    if (!el) return;
    if (state.error) {
      el.hidden = false;
      el.textContent = t("loadError");
      return;
    }
    var page = document.body.dataset.page;
    var needs = page === "home" || page === "works" || page === "work";
    if (needs && !state.ready) {
      el.hidden = false;
      el.textContent = t("loading");
      return;
    }
    el.hidden = true;
    el.textContent = "";
  }

  function applyTitle() {
    if (document.body.dataset.page === "work" && state.ready && !state.error) return;
    var title = state.lang === "en" ? document.body.dataset.titleEn : document.body.dataset.titleZh;
    if (title) document.title = title;
  }

  function applyChrome() {
    document.documentElement.lang = state.lang === "en" ? "en" : "zh-CN";
    document.documentElement.dataset.lang = state.lang;
    document.querySelectorAll("[data-i18n]").forEach(function (node) {
      var value = t(node.dataset.i18n);
      if (value) node.textContent = value;
    });
    document.querySelectorAll("[data-i18n-aria]").forEach(function (node) {
      var value = t(node.dataset.i18nAria);
      if (value) node.setAttribute("aria-label", value);
    });
    document.querySelectorAll("[data-lang-set]").forEach(function (button) {
      button.setAttribute("aria-pressed", button.dataset.langSet === state.lang ? "true" : "false");
    });
    var dialog = document.getElementById("lightbox");
    if (dialog) dialog.setAttribute("aria-label", t("lightbox"));
    applyTitle();
    renderStatus();
  }

  function setLang(lang) {
    if (lang !== "zh" && lang !== "en") return;
    state.lang = lang;
    try { localStorage.setItem("ai-portfolio-lang", lang); } catch (error) { /* ignore */ }
    applyChrome();
    if (state.ready && !state.error) render();
  }

  function filterUrl(tag) {
    var base = window.location.pathname + window.location.search;
    if (tag === "all") return base;
    return base + "#" + encodeURIComponent(tag);
  }

  function tagFromHash() {
    var raw = "";
    try { raw = decodeURIComponent(window.location.hash.replace(/^#/, "")); }
    catch (error) { raw = ""; }
    if (!raw) return "all";
    return tagAllowed(raw) ? raw : "all";
  }

  function setFilter(tag, mode) {
    if (!tagAllowed(tag)) tag = "all";
    if (tag === state.filter) return;
    state.filter = tag;
    if (mode === "push") history.pushState(null, "", filterUrl(tag));
    render();
  }

  function bindLang() {
    document.querySelectorAll("[data-lang-set]").forEach(function (button) {
      button.addEventListener("click", function () { setLang(button.dataset.langSet); });
    });
  }

  function bindFilters() {
    var group = document.getElementById("filters");
    if (!group || group.dataset.bound) return;
    group.dataset.bound = "1";
    group.addEventListener("click", function (event) {
      var button = event.target.closest("[data-tag]");
      if (!button) return;
      setFilter(button.dataset.tag, "push");
    });
    group.addEventListener("keydown", function (event) {
      var keys = ["ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp", "Home", "End"];
      if (keys.indexOf(event.key) === -1) return;
      var radios = Array.prototype.slice.call(group.querySelectorAll("[role='radio']"));
      var current = radios.indexOf(document.activeElement);
      if (current < 0 || !radios.length) return;
      event.preventDefault();
      var next = current;
      if (event.key === "Home") next = 0;
      else if (event.key === "End") next = radios.length - 1;
      else if (event.key === "ArrowLeft" || event.key === "ArrowUp") next = (current - 1 + radios.length) % radios.length;
      else next = (current + 1) % radios.length;
      var tag = radios[next].dataset.tag;
      setFilter(tag, "push");
      var again = group.querySelector('[data-tag="' + tag + '"]');
      if (again) again.focus();
    });
  }

  function bindLightbox() {
    var dialog = document.getElementById("lightbox");
    if (!dialog || dialog.dataset.bound) return;
    dialog.dataset.bound = "1";
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) dialog.close();
    });
    document.getElementById("lb-close").addEventListener("click", function () { dialog.close(); });
    document.getElementById("lb-prev").addEventListener("click", function () { stepLightbox(-1); });
    document.getElementById("lb-next").addEventListener("click", function () { stepLightbox(1); });
    dialog.addEventListener("keydown", function (event) {
      if (event.key === "ArrowRight") { event.preventDefault(); stepLightbox(1); }
      if (event.key === "ArrowLeft") { event.preventDefault(); stepLightbox(-1); }
    });
  }

  function loadWorks() {
    return fetch("works.json").then(function (response) {
      if (!response.ok) throw new Error(String(response.status));
      return response.json();
    }).then(function (data) {
      var list = Array.isArray(data) ? data : (data && data.works);
      if (!Array.isArray(list)) throw new Error("shape");
      state.works = list;
    });
  }

  function init() {
    state.lang = document.documentElement.dataset.lang === "en" ? "en" : "zh";
    bindLang();
    bindFilters();
    bindLightbox();
    applyChrome();
    var page = document.body.dataset.page;
    if (page === "works") {
      window.addEventListener("hashchange", function () {
        var tag = tagFromHash();
        if (tag === state.filter) return;
        state.filter = tag;
        if (state.ready) render();
      });
    }
    if (page === "home" || page === "works" || page === "work") {
      loadWorks().then(function () {
        state.ready = true;
        state.error = false;
        if (page === "works") state.filter = tagFromHash();
        applyChrome();
        render();
      }).catch(function () {
        state.ready = true;
        state.error = true;
        applyChrome();
      });
    }
  }

  init();
})();
