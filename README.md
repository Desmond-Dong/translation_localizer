# Translation Localizer

一个为 Home Assistant 设计的自动化翻译工具，专门用于将自定义组件的界面从英文翻译成中文。

## 功能特性

- 🌐 **自动翻译**: 自动扫描并翻译所有缺少中文翻译的自定义组件
- 🤖 **AI 驱动**: 使用智谱 AI (GLM-4) 提供高质量翻译服务
- 🛡️ **智能保护**: 自动识别并保护 UI 占位符、变量等不应翻译的内容
- 📁 **批量处理**: 一次性处理所有自定义组件，提高效率
- 🎯 **精确翻译**: 专门针对 Home Assistant 界面文本进行优化

## 系统要求

- Home Assistant 版本: 2025.10.0 或更高版本
- Python 依赖: requests>=2.25.0
- 智谱 AI API 密钥

## 安装方法

### 通过 HACS 安装 (推荐)

1. 在 Home Assistant 中打开 HACS
2. 点击"集成"
3. 点击右上角的三个点，选择"自定义存储库"
4. 添加仓库 URL 并选择"集成"
5. 在列表中找到"Translation Localizer"并点击安装
6. 重启 Home Assistant

### 手动安装

1. 下载最新版本的 `translation_localizer.zip`
2. 在 Home Assistant 配置目录中创建 `custom_components/translation_localizer` 文件夹
3. 解压 zip 文件内容到该文件夹
4. 重启 Home Assistant

## 配置方法

### 1. 获取智谱 AI API 密钥

1. 访问 [智谱 AI 官网](https://www.bigmodel.cn/claude-code?ic=19ZL5KZU1F)
2. 注册并登录账号
3. 在控制台中获取 API 密钥

### 2. 配置集成

1. 在 Home Assistant 中进入"设置" > "设备与服务"
2. 点击右下角的"+ 添加集成"
3. 搜索"Translation Localizer"
4. 输入智谱 AI API 密钥
5. 可选: 自定义组件路径 (默认为 "custom_components")
6. 点击"提交"

## 使用方法

### 手动触发翻译

1. 在 Home Assistant 中进入"开发者工具" > "服务"
2. 选择服务: `translation_localizer.translate_components`
3. 点击"调用服务"

### 自动化翻译

可以在 Home Assistant 自动化中定期触发翻译服务:

```yaml
automation:
  - alias: "每周自动翻译新组件"
    trigger:
      - platform: time
        at: "00:00:00"
        days: mon
    action:
      - service: translation_localizer.translate_components
```

## 工作原理

1. **扫描组件**: 扫描指定目录下的所有自定义组件
2. **检查翻译状态**: 检查每个组件是否已有中文翻译文件
3. **识别待翻译组件**: 找出只有英文翻译但缺少中文翻译的组件
4. **智能翻译**: 使用智谱 AI API 翻译文本，同时保护占位符
5. **生成翻译文件**: 创建 `translations/zh-Hans.json` 文件

## 翻译规则

### 自动保护的占位符格式

- `{placeholder}` - 大括号变量
- `%variable%` - 百分号变量
- `${variable}` - 美元符号变量
- `#entity` - 井号实体
- `{{ template }}` - 模板语法

### 支持的翻译内容

- 按钮文本
- 标签和描述
- 错误消息
- 配置选项
- 帮助文本

## 文件结构

```
custom_components/translation_localizer/
├── __init__.py                # 主要集成逻辑
├── manifest.json               # 组件元数据
├── const.py                    # 常量定义
├── config_flow.py              # 配置流程
├── services.yaml               # 服务定义
├── strings.json                # 英文界面文本
└── translations/
    ├── en.json                 # 英文翻译
    └── zh-Hans.json            # 中文翻译
```

## 配置选项

| 配置项 | 必需 | 描述 | 默认值 |
|--------|------|------|--------|
| 智谱 AI API 密钥 | 是 | 用于翻译服务的 API 密钥 | - |
| 自定义组件路径 | 否 | 自定义组件的目录路径 | "custom_components" |

## 故障排除

### 常见问题

**Q: 翻译服务调用失败**
A: 检查智谱 AI API 密钥是否正确，网络连接是否正常

**Q: 某些组件没有被翻译**
A: 确保组件包含 `translations/en.json` 文件且不包含 `translations/zh-Hans.json` 文件

**Q: 翻译质量不佳**
A: 可以手动编辑生成的 `zh-Hans.json` 文件来调整翻译

### 日志查看

在 Home Assistant 中查看相关日志:

1. 进入"设置" > "日志"
2. 筛选"translation_localizer"
3. 查看详细的翻译过程和错误信息

## 开发信息

### API 端点

- **服务**: `translation_localizer.translate_components`
- **描述**: 翻译所有有英文翻译但缺少中文翻译的组件
- **参数**: 无

### 技术实现

- **翻译引擎**: 智谱 AI GLM-4-Flash 模型
- **API 版端**: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- **占位符保护**: 使用正则表达式识别和保留技术元素
- **递归处理**: 支持嵌套 JSON 结构的翻译

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持智谱 AI 翻译
- 自动占位符保护
- HACS 集成支持

## 支持

如果您在使用过程中遇到问题，请:

1. 查看 [常见问题解答](#故障排除)
2. 搜索现有的 [GitHub Issues](https://github.com/your-username/translation-localizer/issues)
3. 创建新的 Issue 描述您的问题

---

**注意**: 本工具仅用于翻译自定义组件的界面文本，不会修改任何功能性代码。翻译完成后请检查生成的翻译文件质量。