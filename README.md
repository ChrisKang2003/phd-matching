# 教授信息爬取系统

基于四层架构（发现 → 抽取 → 归一化 → 更新）的教授信息爬取系统，支持从多个学校、多个系批量爬取教授信息。

## 系统架构

详细架构设计请参考 [ARCHITECTURE.md](ARCHITECTURE.md)

### 核心模块

1. **Discovery（发现层）** - 发现faculty页面URL
2. **Fetcher（抓取器）** - 静态/动态网页抓取
3. **Parser（解析器）** - HTML解析和数据提取
4. **Normalization（归一化层）** - 数据标准化和去重
5. **Storage（存储层）** - 分层数据存储
6. **Update（更新层）** - 增量更新和变更检测
7. **Scheduler（调度器）** - 任务队列和调度

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

编辑 `config.json` 文件，配置要爬取的学校和系：

```json
{
  "universities": [
    {
      "name": "清华大学",
      "code": "THU",
      "discovery": {
        "enabled": true
      },
      "departments": [
        {
          "name": "计算机科学与技术系",
          "code": "CS",
          "faculty_list_url": "https://www.tsinghua.edu.cn/cs/faculty",
          "adapter": null,
          "enabled": true
        }
      ]
    }
  ]
}
```

## 使用方法

### 基本使用

```bash
python main.py
```

### 指定配置文件

```bash
python main.py -c custom_config.json
```

## 数据存储

爬取的数据存储在 `data/` 目录下：

```
data/
├── raw_pages/          # 原始HTML页面
│   └── {university}/{department}/
├── entities/           # 实体数据
│   └── professors.json
├── relations/          # 关系数据
│   ├── professor_department.json
│   ├── professor_publication.json
│   └── professor_lab.json
└── versions/           # 版本数据（用于回溯）
    └── {university}/{department}/
```

## 功能特性

### 1. 自动发现
- 从配置文件读取学校、系、URL列表
- 支持启用/禁用特定学校或系

### 2. 智能抓取
- 优先使用静态抓取（快速）
- 自动检测需要JS渲染的页面，切换到动态抓取
- 支持重试和错误处理

### 3. 通用解析
- 基于语义DOM特征的通用解析规则
- 支持站点特定适配器（可扩展）
- 提取结构化字段和文本字段

### 4. 数据归一化
- 职称统一（Professor/Associate Professor等）
- 部门名称规范化
- 姓名解析（处理中间名、缩写）
- 邮箱还原（处理各种隐藏格式）
- 实体消歧（合并重复记录）

### 5. 增量更新
- 列表页：每14天更新一次
- 个人页：每60天更新一次
- 变更检测：通过hash检测内容变化
- 只更新变化的内容

### 6. 任务调度
- 优先级队列（新学校 > 列表页 > 个人页）
- 并发控制（可配置）
- 重试机制（指数退避）
- 黑名单机制

## 配置说明

### Scheduler配置

```json
"scheduler": {
  "max_concurrent_departments": 3,  // 最大并发数
  "retry_times": 3,                  // 重试次数
  "retry_delay": 5,                  // 重试延迟（秒）
  "delay_between_requests": 2        // 请求间隔（秒）
}
```

### Fetcher配置

```json
"fetcher": {
  "prefer_static": true,      // 优先使用静态抓取
  "timeout": 30,              // 超时时间（秒）
  "retry_times": 3,           // 重试次数
  "wait_for_load": true,      // 等待页面加载
  "wait_timeout": 10000       // 等待超时（毫秒）
}
```

### Parser配置

```json
"parser": {
  "use_llm_fallback": false,        // 是否使用LLM辅助
  "confidence_threshold": 0.7       // 置信度阈值
}
```

### Update配置

```json
"update": {
  "list_page_interval_days": 14,    // 列表页更新间隔（天）
  "profile_page_interval_days": 60, // 个人页更新间隔（天）
  "enable_change_detection": true    // 启用变更检测
}
```

### Storage配置

```json
"storage": {
  "save_raw_html": true,      // 保存原始HTML
  "save_screenshot": false,   // 保存截图
  "save_metadata": true        // 保存元数据
}
```

## 扩展开发

### 添加站点适配器

在 `Web_analys/parser/site_adapters/` 目录下创建新的适配器：

```python
from parser.base_parser import BaseParser

class CustomAdapter(BaseParser):
    def parse(self, html: str, url: str) -> Dict[str, Any]:
        # 实现特定站点的解析逻辑
        pass
    
    def get_confidence(self, html: str, url: str) -> float:
        # 返回置信度
        return 0.9
```

然后在配置文件中指定适配器：

```json
{
  "departments": [
    {
      "name": "计算机系",
      "faculty_list_url": "https://example.com/faculty",
      "adapter": "custom_adapter",
      "enabled": true
    }
  ]
}
```

## 日志

日志文件保存在 `logs/` 目录下：

- `professor_crawler.log` - 主程序日志

## 注意事项

1. **反爬虫**：系统已实现反检测功能，但仍需注意：
   - 控制请求频率
   - 遵守网站的robots.txt
   - 不要过度频繁访问

2. **数据质量**：
   - 归一化层对匹配准确率影响很大
   - 建议定期检查实体消歧结果
   - 可以手动调整解析规则

3. **性能优化**：
   - 优先使用静态抓取
   - 合理设置并发数
   - 启用变更检测避免重复解析

## 故障排除

### 浏览器连接失败
- 确保Chrome或Edge浏览器已安装
- 检查浏览器调试端口是否正确
- 尝试手动启动浏览器并启用远程调试

### 解析失败
- 检查HTML结构是否变化
- 考虑添加站点特定适配器
- 降低置信度阈值

### 存储空间不足
- 可以关闭截图保存
- 定期清理旧版本数据
- 只保存必要的元数据

## 后续开发

- [ ] LLM辅助解析
- [ ] 向量搜索索引
- [ ] 数据导出功能
- [ ] Web界面
- [ ] 监控和报告

## 许可证

MIT License
