# 个人科研绘图图库工作流

## 添加图片

把图片复制到 `figure_gallery/00_inbox/`，或按明确分类放入 `01_minimal`、`02_algorithm`、`03_visual_narrative`、`04_my_favorites`、`05_my_work`。系统不会修改原图，也不会因为图片好看就自动标记为 favorite。

## 扫描与增量索引

在项目根目录运行：

```powershell
python tools/update_gallery.py
```

扫描器使用相对路径和 SHA-256 识别新增、变化和重复图片，把程序估计写入 `gallery_index.csv`，把确定性设计笔记写入 `figure_gallery/_generated/gallery_notes/`。新图片的 `visual_analysis_status` 是 `not_analyzed`；内容变化标记为 `stale` 并把旧记录写入 `_generated/gallery_history/`，空图库会得到空索引，绘图仍使用默认设计系统。

## 设计档案与评价

每张图的笔记只能写可观察事实：类型、布局、留白、颜色关系、字体层级、线条和标注方法。不能从图片推断原始数据、科研结论或字体精确名称。来源、版权说明和用户评价由用户补充；用户明确认可后再把图片复制或移动到 favorites，移动操作由用户自行完成。

如果 Agent 实际打开了图片并完成视觉检查，使用 `GalleryIndex.record_agent_analysis(..., viewed=True, view_receipt=...)` 显式写入观察。记录保存在 `_generated/gallery_visual_analysis/`，重新扫描不会覆盖它；没有实际查看的图片不能标记为 `agent_reviewed`。

## 检索

可在 Python 中按关键词和类别检索：

```python
from figure_studio.gallery import GalleryIndex

gallery = GalleryIndex("figure_gallery")
gallery.scan()
matches = gallery.search(query="convergence", style="algorithm_research")
for record in matches:
    print(record.relative_path, record.style)
```

`search_references()` 会优先返回用户明确 favorite、与图表类型/应用场景匹配且已完成视觉分析的少量记录；它只提供设计参考，不强迫 renderer 复用旧布局。

已明确认可的作品关联可以单独检索，不会被混入图片 favorite：

```powershell
python tools/manage_figure_work.py works --gallery-root figure_gallery --query "算法"
```

返回记录包含 accepted work 的视觉设计回执、入口脚本、配置、版本/任务/复现 manifest 和源文件哈希；如果关联目录失效则不作为可用作品返回。

## 认可作品

生成目录默认是 workspace。验收时先用 `--version-status candidate` 生成候选，再由用户明确提供评价：

```powershell
python tools/manage_figure_work.py accept --candidate-dir path/to/candidate --accepted-dir path/to/accepted --user-note "我认可这版面板层级"
python tools/manage_figure_work.py clone --accepted-dir path/to/accepted --workspace-dir path/to/new-workspace
```

认可作品的 `plot.py`、`config.py`、输入、输出、`version_manifest.json` 和复现 manifest 保持关联；普通重新生成、`--overwrite` 和 snapshot restore 都不会改写认可目录，也不会自动提取模板。

绘图时把检索结果作为设计参考输入，借鉴信息层级和可复现的视觉方法；不要复制参考图中的数据或结论。

## 清理失效索引

先确认图片路径确实失效，再删除 `gallery_index.csv` 中对应记录或 `_generated` 中的笔记。不要删除图库原图；如需重新建立索引，重新运行 `update_gallery.py`。
