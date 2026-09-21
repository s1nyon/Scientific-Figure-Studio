# 字体规范

项目默认使用清晰的无衬线字体。运行时通过 `figure_studio.fonts.resolve_fonts()` 检测实际安装情况，英文优先 Arial、Calibri、Aptos 或 DejaVu Sans，中文优先 Noto Sans SC、Microsoft YaHei、SimHei 或 Source Han Sans SC。

配置中的字体名称不代表机器一定安装。字体检测会返回实际选择、缺失候选和警告。若中文字体没有被确认，必须查看中文测试图，不能只根据代码判断没有乱码。

PDF 使用 TrueType 字体设置，SVG 保留文本节点，方便后续编辑和检索。数学表达式使用 Matplotlib mathtext，不要求系统安装 LaTeX。
