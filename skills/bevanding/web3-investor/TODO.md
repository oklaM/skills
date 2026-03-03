# Web3 Investor Skill - Known Issues & TODO

## Version: 0.1.0-demo

**Status**: Demo ready, known limitations documented below.

---

## Known Issues (暂停存档)

### 1. DefiLlama API Data Parsing Issues

**Problem**: 
- `analyze_protocol.py` 返回的数据不完整
- 某些字段（TVL, chains, category）可能为空或格式不一致
- DefiLlama API 的 `/protocol/{slug}` 端点返回结构因协议而异

**Root Cause**:
- DefiLlama API 没有严格的 schema
- 不同协议的数据结构差异大
- 某些旧协议缺少字段

**Current Workaround**:
- 使用 `--output json` 查看原始数据
- 对空值做默认处理

**TODO**:
- [ ] 添加数据验证和清洗层
- [ ] 针对主流协议（Aave, Compound, Uniswap 等）做特殊处理
- [ ] 添加更多错误处理和 fallback 逻辑

**Priority**: Medium

---

### 2. Risk Scoring Algorithm Accuracy

**Problem**:
- 风险评分算法过于简单
- Uniswap V4 新池子（TVL < $20k）被误评为 LOW risk
- 缺少对协议类型、代币类型的区分

**Root Cause**:
- 当前算法仅基于：审计数量、TVL、是否有治理代币
- 缺少对以下因素的考量：
  - 协议类型（借贷 vs DEX vs 衍生品）
  - 底层资产风险（稳定币 vs 山寨币）
  - 流动性深度
  - 智能合约复杂度
  - 历史漏洞/攻击记录

**Current Workaround**:
- 用户需自行判断，不要完全依赖风险评分
- 结合 TVL 和 APY 做综合判断

**TODO**:
- [ ] 重构风险评分框架，增加更多维度
- [ ] 添加代币类型分析（stablecoin vs volatile）
- [ ] 集成外部风险数据源（如 DeFi Safety）
- [ ] 添加流动性风险评分

**Priority**: High (但 Demo 阶段可接受)

---

### 3. Portfolio Indexer Limited Functionality

**Problem**:
- 只能查询已知代币余额
- 无法获取 DeFi 持仓（借贷、质押等）
- 无法获取 NFT 价值

**Root Cause**:
- 简单 RPC 查询无法覆盖复杂 DeFi 交互
- 需要解析各协议的特定合约

**Current Workaround**:
- 配置 Debank API Key 可获取完整数据
- Demo 阶段仅展示基础代币余额

**TODO**:
- [ ] 集成更多协议的持仓解析（Aave, Compound, Uniswap LP 等）
- [ ] 添加 NFT 估值功能
- [ ] 优化 Debank API 集成

**Priority**: Medium

---

## Future Enhancements (Future TODO)

### Phase 2 - Enhanced Discovery
- [ ] MCP Server 集成（搜索并测试可用的 Web3 MCP 服务器）
- [ ] 多链支持（Arbitrum, Optimism, Base）
- [ ] 社交情绪分析（Twitter, Discord 活跃度）
- [ ] 链上数据分析（大户持仓、资金流向）

### Phase 2 - Trading Automation
- [ ] Phase 2 实现：限额内自动执行
- [ ] Safe{Wallet} 多签集成
- [ ] 交易历史记录和分析
- [ ] Gas 优化策略

### Phase 3 - Full Autonomy
- [ ] Phase 3 实现：完全自主投资
- [ ] 安全审计
- [ ] 保险机制
- [ ] 回撤控制

---

## Contributing

If you encounter issues not listed here, please:
1. Check the error message
2. Try the workarounds above
3. Submit an issue with reproduction steps

---

**Last Updated**: 2026-03-03
**Maintainer**: Web3 Investor Skill Team