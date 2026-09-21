param(
    [string]$CondaExe = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($CondaExe)) {
    $condaCommand = Get-Command conda -ErrorAction SilentlyContinue
    if (-not $condaCommand) {
        throw "找不到 conda。请先安装用户范围的 Miniconda 或 Miniforge，或使用 -CondaExe 指定 conda.bat。"
    }
    $CondaExe = $condaCommand.Source
}

$packages = @(
    "python=3.11",
    "matplotlib>=3.8",
    "numpy>=1.26",
    "pandas>=2.1",
    "pillow>=10.0",
    "pyyaml>=6.0",
    "pypdf>=4.0",
    "pytest>=8.0",
    "ruff>=0.6"
)

$envListJson = & $CondaExe env list --json | ConvertFrom-Json
$existingEnvironment = @($envListJson.envs) | Where-Object {
    $_ -match "[\\/]scientific-figure-studio$"
}
if ($existingEnvironment) {
    Write-Host "Conda 环境 scientific-figure-studio 已存在：$existingEnvironment"
    exit 0
}

& $CondaExe create --override-channels -c conda-forge -n scientific-figure-studio @packages --yes
if ($LASTEXITCODE -ne 0) {
    throw "Conda 环境创建失败，退出码：$LASTEXITCODE"
}
