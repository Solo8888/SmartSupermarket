# 智能超市大数据平台

一个基于Docker容器化的智能超市大数据分析平台，集成了Hadoop、Spark、Hive等大数据技术栈，提供完整的超市业务数据分析和可视化功能。

## 🚀 技术栈

### 大数据基础设施
- **Hadoop 3.3.6** - 分布式存储和计算框架 (HDFS + YARN)
- **Spark 3.5.3** - 快速的大数据处理框架 (批处理 + 流处理 + ML)
- **Hive 3.1.3** - 数据仓库解决方案
- **Kafka** - 分布式消息队列

### 数据库与缓存
- **MySQL 8.0** - 关系型业务数据库
- **PostgreSQL 11** - Hive元数据存储
- **Redis** - 高性能缓存

### Web应用框架
- **Flask** - Python Web后端框架
- **Vue.js 3** - 桌面端Web前端框架
- **Vite** - 前端构建工具

### 开发工具
- **Jupyter Notebook** - 交互式数据分析环境
- **Docker & Docker Compose** - 容器化部署

## 📋 系统架构

本项目采用微服务架构，包含以下核心组件：

- **Hadoop集群**：1个Master节点 + 2个Worker节点
- **Spark集群**：集成在Hadoop集群中
- **数据存储层**：MySQL(业务数据) + PostgreSQL(Hive元数据) + Redis(缓存)
- **消息队列**：Kafka + Zookeeper
- **Web应用层**：Flask后端 + Vue.js前端
- **数据分析**：Jupyter Notebook

## 🛠️ 环境要求

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **内存**：建议8GB以上
- **磁盘空间**：建议20GB以上

## 🚀 快速启动

### 方式一：使用预构建镜像（推荐，避免国内网络问题）
由于国内访问Docker Hub可能受限，项目提供了分卷压缩的预构建镜像，使用Git LFS管理：

1. **克隆仓库并下载LFS文件**：
   ```bash
   git clone <repository-url>
   cd SmartSupermarket
   git lfs pull
   ```

2. **还原Docker镜像**：
   
   **Windows系统**:
   ```powershell
   .\restore-images.ps1
   ```
   
   **Linux/macOS系统**:
   ```bash
   chmod +x restore-images.sh
   ./restore-images.sh
   ```

3. **启动所有服务**：
   ```bash
   docker-compose up -d
   ```

### 方式二：使用Make命令（需要良好网络）
```bash
# 构建所有Docker镜像并启动服务
make
```

### 方式三：分步启动
```bash
# 1. 构建基础镜像
make all

# 2. 启动所有服务
docker-compose up -d
```

### 方式四：使用Windows批处理文件
```bash
# Windows系统下使用
make.bat
```

## 🌐 服务访问地址

### Hadoop集群管理界面
- **ResourceManager**：http://localhost:8088
- **NameNode**：http://localhost:9870
- **HistoryServer**：http://localhost:19888
- **DataNode1**：http://localhost:9864
- **DataNode2**：http://localhost:9865
- **NodeManager1**：http://localhost:8042
- **NodeManager2**：http://localhost:8043

### Spark集群管理界面
- **Spark Master**：http://localhost:8080
- **Spark Worker1**：http://localhost:8081
- **Spark Worker2**：http://localhost:8082
- **Spark History**：http://localhost:18080

### 数据库服务
- **Hive JDBC**：jdbc:hive2://localhost:10000
- **MySQL**：localhost:3306 (用户: supermarket_user, 密码: Emma19900415)
- **PostgreSQL**：localhost:5432 (密码: jupyter)
- **Redis**：localhost:6379

### 开发工具
- **Jupyter Notebook**：http://localhost:8888
- **Kafka**：localhost:9093

### Web应用
- **前端应用**：http://localhost:3000
- **后端API**：http://localhost:5000

## 📁 项目结构

```
SmartSupermarket/
├── backend/              # Flask后端应用
│   ├── app.py           # 主应用文件
│   ├── requirements.txt # Python依赖
│   └── Dockerfile       # 后端镜像配置
├── base/                 # 基础镜像配置
│   ├── conf/            # Hadoop/Spark/Hive配置文件
│   ├── Dockerfile       # 基础镜像配置
│   └── entrypoint.sh    # 启动脚本
├── frontend/            # Vue.js前端应用
│   ├── src/             # 源代码目录
│   ├── package.json     # 前端依赖
│   └── Dockerfile       # 前端镜像配置
├── history/             # Spark历史服务器配置
│   ├── Dockerfile
│   └── run.sh
├── jupyter/             # Jupyter Notebook配置
│   ├── notebook/        # 示例笔记本
│   ├── Dockerfile
│   └── run.sh
├── master/              # Hadoop主节点配置
│   ├── Dockerfile
│   └── run.sh
├── metastore/           # Hive元数据存储配置
│   └── ddl/init.sql     # 数据库初始化脚本
├── worker/              # Hadoop从节点配置
│   ├── Dockerfile
│   └── run.sh
├── docker-compose.yml   # 容器编排配置
├── Makefile             # 自动化构建脚本
├── make.bat             # Windows构建脚本
├── restore-images.ps1    # Windows镜像还原脚本
├── restore-images.sh     # Linux/macOS镜像还原脚本
├── .env                 # 环境变量配置
└── README.md            # 项目说明文档
```

## 🔧 开发指南

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 数据分析开发
访问 http://localhost:8888 进入Jupyter Notebook环境，使用PySpark进行数据分析。

## ⚙️ 配置说明

### 环境变量配置 (.env)
```bash
MYSQL_ROOT_PASSWORD=Emma19900415
MYSQL_DATABASE=smart_supermarket
MYSQL_USER=supermarket_user
MYSQL_PASSWORD=Emma19900415
```

### 网络配置
项目使用自定义网络 `sparknet` (子网: 172.28.0.0/16)，各服务分配固定IP地址。

## 📊 功能特性

- **数据采集**：支持多种数据源接入
- **数据存储**：分布式存储与关系型存储结合
- **数据处理**：批处理与流处理能力
- **数据分析**：交互式数据探索
- **数据可视化**：实时数据展示
- **系统监控**：集群状态监控

## 🔒 安全注意事项

- 本项目仅用于学习和开发环境
- 生产环境请修改默认密码和配置
- 确保Docker环境安全配置
- 定期备份重要数据

## 🐛 故障排除

### 常见问题
1. **端口冲突**：检查端口是否被占用
2. **内存不足**：增加Docker内存分配
3. **启动失败**：查看容器日志 `docker logs <container_name>`

### 日志查看
```bash
# 查看所有容器状态
docker-compose ps

# 查看特定容器日志
docker-compose logs <service_name>

# 实时查看日志
docker-compose logs -f <service_name>
```

### 重启服务
```bash
# 重启单个服务
docker-compose restart <service_name>

# 重启所有服务
docker-compose restart
```

## 📄 许可证

本项目仅用于学习和研究目的。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

---

**注意**：首次启动时，各服务需要一定时间进行初始化，请耐心等待。如需自定义配置，请修改对应服务的配置文件。