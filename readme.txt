国际人工智能公共产品服务水平观测台

运行验收：
python3 -m public_service_sla run --fixture fixtures/acceptance.json --database /tmp/public_service_sla.sqlite3 --output /tmp/public_service_sla-output

核验：
python3 -m public_service_sla verify --database /tmp/public_service_sla.sqlite3 --output /tmp/public_service_sla-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.sla_signal.test_sla_pressure -v
python3 -m unittest tests.diagnostics.test_stratified_diagnostics -v

构建检查：
python3 -m compileall -q public_service_sla tests

地区与用户群体分层诊断（public_service_sla/diagnostics/stratified_diagnostics.py）：
- 同一批服务窗口遥测按 region_code 与 user_group 两个维度分层，逐层比较请求负荷
  （request_queue/resource_load）、有效响应（response_ms 在预算内的占比）、异常率
  （error_rate 超阈占比，并单列记录缺陷率）和容量占用（queue/capacity）。
- 证据状态只有 trusted 与 insufficient_evidence 两种。样本量不足、关键字段覆盖率不够或
  缺少可信数值观测的分层一律标记为证据不足，建议固定为 insufficient_evidence，
  绝不据此给出“正常”结论或扩容建议。
- 修复建议区分三类失约根因：队列激增且容量饱和才定向扩容（add_capacity_targeted）；
  记录异常先修遥测（fix_records_and_instrumentation）；持续失约但容量有余量则保障
  弱势群体（protect_user_group）。总体均值不再掩盖分层差异，弱势分层会进入
  vulnerable_strata，并在修复决策中被保守地转为 review。
- 该诊断在一次 run 内只计算一次，修复决策（routing_flow.decide）与报告
  （summary.json 的 stratified_diagnostics、stratified-diagnostics.csv）共享同一证据；
  未提供诊断上下文时决策引擎行为与旧版本完全一致，旧记录、决策与审计链仍可核验。

