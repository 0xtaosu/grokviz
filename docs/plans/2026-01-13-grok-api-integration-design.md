# GrokViz 架构重构：从邮件监控到 Grok API 直接调用

**日期**: 2026-01-13
**状态**: 已批准
**作者**: Claude Code

## 概述

将 GrokViz 从"监控邮件获取报告"的架构重构为"直接调用 Grok API 生成报告"的架构。这是一个重大的架构变更，但采用最小改动方案，保留现有的信息图生成和 Telegram 分发模块。

## 背景

**原有架构问题**：
- 依赖邮件服务器认证（Outlook 认证复杂，需要 2FA/应用密码）
- 邮件监控增加了不必要的复杂度
- 实时性受限于邮件接收延迟

**新方案优势**：
- 直接调用 xAI Grok API，无需邮件中转
- 更可控的触发机制（定时 + 手动）
- 减少外部依赖，提高稳定性

## 架构设计

### 1. 架构概览

#### 移除的模块
- `src/email_monitor/` - 整个邮件监控模块
- 相关配置：`EMAIL_SERVER`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `GROK_SENDER_EMAIL`

#### 新增的模块
- `src/grok_client/` - Grok API 客户端
  - `client.py` - 调用 xAI Grok API
  - `prompts.py` - 提示词管理
  - 支持重试逻辑和错误处理

#### 保留的模块（几乎不变）
- `src/data_processor/` - 处理 Grok 返回的 JSON 数据
- `src/infographic/` - 使用 Gemini 生成信息图
- `src/telegram/` - 发送到 Telegram
- `src/utils/` - 日志和错误处理

#### 修改的文件
- `src/main.py` - 主流程：从调用邮件改为调用 Grok API
- `src/config.py` - 配置管理：移除邮件配置，添加 Grok API 配置
- `.env` - 环境变量：添加 `GROK_API_KEY`
- `requirements.txt` - 依赖保持不变（使用 requests 调用 API）

#### 新的工作流程

```
1. 调用 Grok API（带加密货币分析提示词）
   ↓
2. 获取结构化 JSON 响应
   ↓
3. 处理和验证数据
   ↓
4. 生成信息图（Gemini）
   ↓
5. 发送到 Telegram
   ↓
6. 归档数据
```

### 2. Grok API 集成模块

#### 模块结构

```python
# src/grok_client/__init__.py
from .client import GrokClient

# src/grok_client/client.py
class GrokClient:
    """xAI Grok API 客户端"""

    def __init__(self, api_key: str, model: str = "grok-beta",
                 max_retries: int = 3, retry_delay: int = 5):
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.base_url = "https://api.x.ai/v1"

    def generate_report(self, prompt: str, timeout: int = 120) -> dict:
        """调用 Grok API 生成报告"""
        # 实现 API 调用逻辑
```

#### API 调用方式

xAI 的 Grok API 兼容 OpenAI 格式：

```
POST https://api.x.ai/v1/chat/completions
Headers:
  Authorization: Bearer {GROK_API_KEY}
  Content-Type: application/json

Body:
{
  "model": "grok-beta",
  "messages": [{"role": "user", "content": "提示词"}],
  "response_format": {"type": "json_object"}
}
```

#### 错误处理

- **401 Unauthorized**: API key 无效，立即失败
- **429 Rate Limit**: 触发限流，指数退避重试
- **500 Server Error**: xAI 服务问题，重试最多 3 次
- **Timeout**: 请求超时（120秒），记录日志并重试

#### 提示词管理

```python
# src/grok_client/prompts.py

CRYPTO_ANALYSIS_PROMPT = """
你是一名顶级的加密货币社交舆情研究员（Social Intelligence Analyst）。你擅长通过 X (Twitter) 的海量数据发现信息差，能够精准区分"大众热议的共识"与"极客圈内的非共识机会"。

请分析过去 24 小时内的推特动态和加密市场数据，生成一份结构化的投研报告。

第一部分：信息搜集与处理逻辑
全域扫描： 扫描 X 上头部的加密新闻媒体（CoinDesk, The Block, Cointelegraph）获取宏观新闻。
KOL 动态监控： 分析顶级 KOL、风投研究员（如 a16z, Paradigm, Vitalik, Toly）及深度开发者社区的最新互动。
情绪分析： 识别当前讨论中最活跃的标签（Hashtags）和叙事逻辑。

第二部分：共识机会（Top 5 Consensus）
定义： 讨论热度极高（Heat Score > 80），多个大 V 同步转发，市场已达成高度一致的利好或赛道。
输出要求：
1. 机会名称： (例如：预测市场、AI Agent)
2. 热度评分： (1-100)
3. 核心共识点： 市场普遍看好的理由。
4. 关键证据： 提及该话题的典型账号或高赞推文链接/摘要。

第三部分：非共识机会（Top 5 Non-Consensus）
定义： 讨论热度尚低（Heat Score 20-50），但在"聪明钱"（Smart Money）或"硬核开发者"圈子中被反复提及。大众尚未察觉，或伴随争议。
输出要求：
1. 机会名称： (例如：新的 L2 结算协议、铭文协议变体)
2. 潜力评分： (1-100)
3. 非共识逻辑： 为什么大V还没开始喊？现在的核心争议或门槛在哪里？
4. 埋伏线索： 你在哪个小众推文或评论区发现了这个苗头？

第四部分：市场宏观与链上指标
主流币表现： BTC/ETH 的价格、24h 涨跌、主要交易所的资金费率（Funding Rate）。
贪婪指数： 引用当天的 Crypto Fear & Greed Index。
社交杠杆： 过去 24h 推特讨论量环比增长最快的三个币种/关键词。

# 输出格式限制
语言： 全中文呈现。
风格： 专业、冷静、数据导向，拒绝空洞的形容词。
结构： 使用 Markdown 标题和表格。
JSON： 在报告末尾，请附带一个紧凑的 JSON 格式块，包含上述共识与非共识机会的字段，以便我存入数据库。
"""
```

### 3. 数据处理变更

#### 数据流变化

**原来**：邮件 HTML/JSON → 解析 → 标准化数据结构
**现在**：Grok API JSON → 验证 → 标准化数据结构

#### JSON 数据格式（Grok 返回）

```json
{
  "date": "2026-01-13",
  "consensus_opportunities": [
    {
      "name": "预测市场",
      "heat_score": 85,
      "core_logic": "市场普遍看好的理由...",
      "evidence": "典型账号或推文摘要..."
    }
  ],
  "non_consensus_opportunities": [
    {
      "name": "新的 L2 结算协议",
      "potential_score": 45,
      "non_consensus_logic": "为什么大V还没开始喊...",
      "clues": "在哪个小众推文发现..."
    }
  ],
  "market_macro": {
    "btc_price": 45000,
    "eth_price": 2500,
    "fear_greed_index": 65,
    "trending_tokens": ["TOKEN1", "TOKEN2", "TOKEN3"]
  }
}
```

#### 数据处理器修改

**`src/data_processor/json_processor.py`** - 更新验证逻辑：
- 移除邮件附件相关代码
- 添加 Grok JSON 格式验证
- 确保必需字段存在：`consensus_opportunities`, `non_consensus_opportunities`, `market_macro`
- 数据清洗：处理缺失值、异常分数（如 heat_score > 100）

**`src/data_processor/html_parser.py`** - 可以删除（不再需要 HTML 解析）

#### 标准化输出格式

```python
{
    "date": "2026-01-13",
    "title": "Grok 加密货币日报",
    "consensus": [...],      # Top 5
    "non_consensus": [...],  # Top 5
    "market_data": {...}
}
```

### 4. 主流程修改（main.py）

#### 原有流程 vs 新流程

**原有流程**：
1. 连接邮件服务器
2. 获取未读邮件
3. 解析邮件内容
4. 提取 JSON/HTML 数据
5. 生成信息图
6. 发送到 Telegram

**新流程**：
1. 调用 Grok API 生成报告
2. 验证返回的 JSON 数据
3. 生成信息图
4. 发送到 Telegram
5. 归档数据

#### 核心代码结构

```python
def main() -> int:
    """主工作流程"""
    start_time = time.time()

    try:
        # 1. 加载配置
        config = Config.from_env()
        setup_logging(config)
        logger = get_logger(__name__)

        logger.info("=" * 60)
        logger.info("GrokViz workflow started")
        logger.info("=" * 60)

        # 2. 初始化组件
        grok_client = GrokClient(
            api_key=config.grok_api_key,
            model=config.grok_model,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        json_processor = JSONProcessor()

        infographic_gen = InfographicGenerator(
            api_key=config.gemini_api_key,
            model_name=config.gemini_model,
            output_dir=config.temp_dir,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        telegram_bot = TelegramBot(
            token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        # 3. 调用 Grok API 生成报告
        logger.info("Calling Grok API to generate crypto analysis report...")
        raw_data = grok_client.generate_report(
            CRYPTO_ANALYSIS_PROMPT,
            timeout=config.grok_timeout
        )
        logger.info("Grok API call successful")

        # 4. 处理和验证数据
        logger.info("Processing and validating data...")
        structured_data = json_processor.process(raw_data)
        logger.info(f"Data processed: {structured_data.get('date')}")

        # 5. 生成信息图
        logger.info("Generating infographic...")
        image_path = infographic_gen.generate(structured_data, timeout=120)
        logger.info(f"Infographic generated: {image_path}")

        # 6. 发送到 Telegram
        logger.info("Sending to Telegram...")
        caption = telegram_bot.format_caption(structured_data)
        message_id = telegram_bot.send_photo(image_path, caption)
        logger.info(f"Sent to Telegram: message_id={message_id}")

        # 7. 归档数据
        if config.archive_reports:
            archive_data(structured_data, image_path, config)

        # 8. 记录成功
        duration = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"Workflow completed successfully in {duration:.2f}s")
        logger.info("=" * 60)

        return 0

    except GrokAPIError as e:
        logger.critical(f"Grok API error: {e}", exc_info=True)
        return 2
    except Exception as e:
        logger.critical(f"Workflow failed: {e}", exc_info=True)
        return 2
```

### 5. 配置更新

#### .env 文件变更

**移除的配置**：
```bash
# 不再需要邮件相关配置
EMAIL_SERVER=...
EMAIL_PORT=...
EMAIL_USERNAME=...
EMAIL_PASSWORD=...
GROK_SENDER_EMAIL=...
```

**新增的配置**：
```bash
# ============================================
# Grok API Configuration
# ============================================
GROK_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxxxxx
GROK_MODEL=grok-beta
GROK_TIMEOUT=120

# ============================================
# Scheduling Configuration
# ============================================
SCHEDULE_HOUR=8  # 每天几点生成报告（可选）
```

**保留的配置**：
```bash
# Gemini API（生成信息图）
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro

# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Application Configuration
LOG_LEVEL=INFO
DATA_DIR=/app/data
TEMP_DIR=/app/data/temp
ARCHIVE_REPORTS=true  # 从 ARCHIVE_EMAILS 改名

# Retry Configuration
MAX_RETRIES=3
RETRY_DELAY=5
```

#### config.py 更新

```python
@dataclass
class Config:
    """Application configuration"""

    # Grok API
    grok_api_key: str
    grok_model: str = "grok-beta"
    grok_timeout: int = 120

    # Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-pro"

    # Telegram
    telegram_bot_token: str
    telegram_chat_id: str

    # Application
    log_level: str = "INFO"
    data_dir: Path = Path("/app/data")
    temp_dir: Path = Path("/app/data/temp")
    archive_reports: bool = True

    # Retry
    max_retries: int = 3
    retry_delay: int = 5

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        return cls(
            grok_api_key=os.getenv("GROK_API_KEY"),
            grok_model=os.getenv("GROK_MODEL", "grok-beta"),
            grok_timeout=int(os.getenv("GROK_TIMEOUT", "120")),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            data_dir=Path(os.getenv("DATA_DIR", "/app/data")),
            temp_dir=Path(os.getenv("TEMP_DIR", "/app/data/temp")),
            archive_reports=os.getenv("ARCHIVE_REPORTS", "true").lower() == "true",
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_delay=int(os.getenv("RETRY_DELAY", "5"))
        )
```

#### requirements.txt

无需修改（继续使用 `requests` 调用 Grok API）

### 6. 部署与调度

#### 本地开发模式

**手动触发**：
```bash
# 设置环境变量
export GROK_API_KEY=xai-xxxxx

# 运行一次
python -m src.main

# 或使用 Docker
docker exec grokviz python -m src.main
```

#### 生产部署（Docker）

**构建和启动**：
```bash
# 1. 更新 .env 文件（添加 GROK_API_KEY，移除邮件配置）
# 2. 重新构建镜像
docker-compose build

# 3. 启动容器
docker-compose up -d

# 4. 查看日志
docker-compose logs -f grokviz
```

#### 定时任务配置

**cron/grokviz-cron** 更新为：
```bash
# 每天早上 8:00 生成报告
0 8 * * * cd /app && python -m src.main >> /var/log/cron.log 2>&1

# 或者每天两次（早8点和晚8点）
0 8,20 * * * cd /app && python -m src.main >> /var/log/cron.log 2>&1
```

#### 健康检查

**scripts/health_check.sh** 需要更新：
```bash
#!/bin/bash
# 检查最近一次报告生成时间
# 如果超过 25 小时没有生成，返回失败

LAST_REPORT=$(find /app/data/temp -name "*.png" -mtime -1 | wc -l)
if [ "$LAST_REPORT" -eq 0 ]; then
    echo "No report generated in the last 24 hours"
    exit 1
fi

echo "Health check passed"
exit 0
```

#### 监控和告警

**日志位置**：
- 应用日志：`data/logs/grokviz.log`
- Cron 日志：`/var/log/cron.log`（容器内）

**关键指标**：
- Grok API 调用成功率（目标 > 99%）
- 信息图生成成功率（目标 > 99%）
- Telegram 发送成功率（目标 > 99%）
- 端到端延迟（目标 < 3 分钟）

## 实施计划

### 阶段 1：准备工作
1. 创建 `src/grok_client/` 模块
2. 实现 `GrokClient` 类
3. 添加提示词到 `prompts.py`
4. 更新 `config.py` 和 `.env.example`

### 阶段 2：核心重构
1. 修改 `src/main.py` 主流程
2. 更新 `src/data_processor/json_processor.py`
3. 删除 `src/email_monitor/` 模块
4. 删除 `src/data_processor/html_parser.py`

### 阶段 3：测试验证
1. 单元测试：测试 Grok API 调用
2. 集成测试：端到端流程测试
3. 手动测试：生成一份完整报告

### 阶段 4：部署上线
1. 更新 Docker 配置
2. 更新 Cron 配置
3. 部署到生产环境
4. 监控运行状态

## 风险与缓解

### 风险 1：Grok API 不稳定
- **缓解**：实现重试逻辑，记录详细日志
- **回退**：保留旧代码分支，可快速回滚

### 风险 2：Grok 返回格式不符合预期
- **缓解**：强制使用 `response_format: json_object`
- **验证**：严格的 JSON schema 验证

### 风险 3：API 成本过高
- **缓解**：监控 API 调用次数和成本
- **优化**：调整 Cron 频率（如从每天2次改为1次）

## 成功标准

- ✅ Grok API 调用成功率 > 99%
- ✅ 端到端延迟 < 3 分钟
- ✅ 生成的报告质量符合预期
- ✅ 定时任务稳定运行
- ✅ 手动触发功能正常

## 附录

### A. Grok API 文档参考
- xAI API 文档：https://docs.x.ai/api
- 兼容 OpenAI 格式

### B. 测试用例
- 测试 Grok API 连接
- 测试 JSON 格式验证
- 测试完整工作流程

### C. 回滚计划
如果新版本有问题：
```bash
# 1. 停止容器
docker-compose down

# 2. 切换到旧版本
git checkout <old-commit>

# 3. 恢复旧的 .env（保留邮件配置）
cp .env.backup .env

# 4. 重新构建和启动
docker-compose build
docker-compose up -d
```
