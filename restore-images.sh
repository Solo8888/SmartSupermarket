#!/bin/bash

# Docker镜像还原脚本
# 用于从Bandizip分卷压缩文件还原Docker镜像

VOLUME_PREFIX="images"
OUTPUT_FILE="images.tar"

echo "=== Docker镜像还原脚本 ==="
echo "开始还原Docker镜像..."

# 检查分卷文件是否存在
volume_files=$(ls ${VOLUME_PREFIX}.t* 2>/dev/null | sort)
if [ -z "$volume_files" ]; then
    echo "错误: 未找到分卷文件 ${VOLUME_PREFIX}.t*"
    echo "请确保所有分卷文件 (${VOLUME_PREFIX}.t01, ${VOLUME_PREFIX}.t02, ...) 都在当前目录"
    exit 1
fi

# 统计分卷文件数量
file_count=$(echo "$volume_files" | wc -w)
echo "找到分卷文件: $file_count 个"
echo "$volume_files" | while read file; do echo "  - $file"; done

# 检查是否已存在目标文件
if [ -f "$OUTPUT_FILE" ]; then
    read -p "目标文件 $OUTPUT_FILE 已存在，是否覆盖? (y/n): " choice
    if [ "$choice" != "y" ] && [ "$choice" != "Y" ]; then
        echo "操作已取消"
        exit 0
    fi
    rm -f "$OUTPUT_FILE"
fi

echo ""
echo "开始合并分卷文件..."

# 方法1: 尝试使用支持分卷的压缩工具
if command -v 7z &> /dev/null; then
    echo "使用7z解压..."
    first_volume="${VOLUME_PREFIX}.t01"
    if 7z x "$first_volume" -y; then
        echo "7z解压成功!"
    else
        echo "7z解压失败，尝试手动合并..."
    fi
fi

# 方法2: 手动合并分卷文件
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "使用cat命令手动合并分卷文件..."
    
    # 检查所有分卷文件是否完整
    for file in $volume_files; do
        if [ ! -f "$file" ]; then
            echo "错误: 分卷文件 $file 不存在"
            exit 1
        fi
    done
    
    # 合并文件
    cat ${VOLUME_PREFIX}.t* > "$OUTPUT_FILE"
    
    if [ $? -eq 0 ]; then
        echo "分卷文件合并完成!"
    else
        echo "合并过程中发生错误"
        rm -f "$OUTPUT_FILE"
        exit 1
    fi
fi

# 验证合并后的文件
if [ -f "$OUTPUT_FILE" ]; then
    file_size=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo "合并完成: $OUTPUT_FILE ($file_size)"
    
    # 加载Docker镜像
    echo ""
    echo "开始加载Docker镜像..."
    
    if ! command -v docker &> /dev/null; then
        echo "警告: 未找到Docker，请先安装Docker"
        echo "镜像文件已生成，可以手动使用命令加载: docker load -i $OUTPUT_FILE"
        exit 0
    fi
    
    echo "执行: docker load -i $OUTPUT_FILE"
    docker load -i "$OUTPUT_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Docker镜像加载成功!"
        echo ""
        echo "可以使用以下命令查看已加载的镜像:"
        echo "  docker images"
    else
        echo "Docker镜像加载失败，请检查Docker服务是否运行"
    fi
else
    echo "错误: 合并后的文件不存在"
    exit 1
fi

echo ""
echo "=== 还原完成 ==="