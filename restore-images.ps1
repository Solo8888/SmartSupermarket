# Docker镜像还原脚本
# 用于从Bandizip分卷压缩文件还原Docker镜像

param(
    [string]$VolumePrefix = "images",
    [string]$OutputFile = "images.tar"
)

Write-Host "=== Docker镜像还原脚本 ===" -ForegroundColor Green
Write-Host "开始还原Docker镜像..." -ForegroundColor Yellow

# 检查是否安装了Bandizip
$bandizipPath = Get-Command "Bandizip" -ErrorAction SilentlyContinue
if (-not $bandizipPath) {
    Write-Host "警告: 未找到Bandizip，请确保已安装Bandizip并添加到PATH环境变量" -ForegroundColor Red
    Write-Host "或者使用其他支持分卷压缩的软件手动解压" -ForegroundColor Yellow
    Write-Host ""
}

# 检查分卷文件是否存在
$volumeFiles = Get-ChildItem "${VolumePrefix}.t*" | Sort-Object Name
if ($volumeFiles.Count -eq 0) {
    Write-Host "错误: 未找到分卷文件 ${VolumePrefix}.t*" -ForegroundColor Red
    Write-Host "请确保所有分卷文件 (${VolumePrefix}.t01, ${VolumePrefix}.t02, ...) 都在当前目录" -ForegroundColor Yellow
    exit 1
}

Write-Host "找到分卷文件: $($volumeFiles.Count) 个" -ForegroundColor Green
$volumeFiles | ForEach-Object { Write-Host "  - $($_.Name)" }

# 检查是否已存在目标文件
if (Test-Path $OutputFile) {
    $choice = Read-Host "目标文件 $OutputFile 已存在，是否覆盖? (y/n)"
    if ($choice -ne 'y' -and $choice -ne 'Y') {
        Write-Host "操作已取消" -ForegroundColor Yellow
        exit 0
    }
    Remove-Item $OutputFile -Force
}

Write-Host ""
Write-Host "开始合并分卷文件..." -ForegroundColor Yellow

# 方法1: 使用Bandizip解压（如果可用）
if ($bandizipPath) {
    Write-Host "使用Bandizip解压..." -ForegroundColor Green
    try {
        $firstVolume = "${VolumePrefix}.t01"
        & Bandizip x "$firstVolume" -o:"." -y
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Bandizip解压成功!" -ForegroundColor Green
        } else {
            Write-Host "Bandizip解压失败，尝试手动合并..." -ForegroundColor Yellow
            throw "Bandizip failed"
        }
    } catch {
        Write-Host "Bandizip解压失败，使用手动合并方法..." -ForegroundColor Yellow
        # 继续使用手动方法
    }
}

# 方法2: 手动合并分卷文件
if (-not (Test-Path $OutputFile)) {
    Write-Host "使用PowerShell手动合并分卷文件..." -ForegroundColor Green
    
    # 创建输出文件流
    $outputStream = [System.IO.File]::Create($OutputFile)
    
    try {
        foreach ($volume in $volumeFiles) {
            Write-Host "处理分卷: $($volume.Name)" -ForegroundColor Cyan
            
            $volumeStream = [System.IO.File]::OpenRead($volume.FullName)
            $buffer = New-Object byte[] 81920
            $bytesRead = 0
            
            do {
                $bytesRead = $volumeStream.Read($buffer, 0, $buffer.Length)
                $outputStream.Write($buffer, 0, $bytesRead)
            } while ($bytesRead -gt 0)
            
            $volumeStream.Close()
        }
        
        Write-Host "分卷文件合并完成!" -ForegroundColor Green
    } catch {
        Write-Host "合并过程中发生错误: $($_.Exception.Message)" -ForegroundColor Red
        $outputStream.Close()
        if (Test-Path $OutputFile) {
            Remove-Item $OutputFile -Force
        }
        exit 1
    } finally {
        $outputStream.Close()
    }
}

# 验证合并后的文件
if (Test-Path $OutputFile) {
    $fileInfo = Get-Item $OutputFile
    Write-Host "合并完成: $($fileInfo.Name) ($([math]::Round($fileInfo.Length / 1GB, 2)) GB)" -ForegroundColor Green
    
    # 加载Docker镜像
    Write-Host ""
    Write-Host "开始加载Docker镜像..." -ForegroundColor Yellow
    
    $dockerCheck = Get-Command "docker" -ErrorAction SilentlyContinue
    if (-not $dockerCheck) {
        Write-Host "警告: 未找到Docker，请先安装Docker Desktop" -ForegroundColor Red
        Write-Host "镜像文件已生成，可以手动使用命令加载: docker load -i $OutputFile" -ForegroundColor Yellow
        exit 0
    }
    
    try {
        Write-Host "执行: docker load -i $OutputFile" -ForegroundColor Cyan
        & docker load -i $OutputFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker镜像加载成功!" -ForegroundColor Green
            Write-Host ""
            Write-Host "可以使用以下命令查看已加载的镜像:" -ForegroundColor Yellow
            Write-Host "  docker images" -ForegroundColor White
        } else {
            Write-Host "Docker镜像加载失败，请检查Docker服务是否运行" -ForegroundColor Red
        }
    } catch {
        Write-Host "Docker命令执行失败: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "错误: 合并后的文件不存在" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== 还原完成 ===" -ForegroundColor Green