国际人工智能公共产品服务水平观测台

运行验收：
python3 -m public_service_sla run --fixture fixtures/acceptance.json --database /tmp/public_service_sla.sqlite3 --output /tmp/public_service_sla-output

核验：
python3 -m public_service_sla verify --database /tmp/public_service_sla.sqlite3 --output /tmp/public_service_sla-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.sla_signal.test_sla_pressure -v

构建检查：
python3 -m compileall -q public_service_sla tests
