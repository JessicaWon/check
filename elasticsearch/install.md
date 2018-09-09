## 安装es
```
我安装的版本比较低，是2.x的版本的
```
## 配置文件
```
配置文件中的东西主要分为两块，一块是mapping，一块是配置文件
```
### 配置文件
```
cluster.name: log_courier
processors: 4
node.name: "IP:9200"
node.master: true
node.data: true
node.max_local_storage_nodes: 1

bootstrap.mlockall: true

threadpool.bulk.type: fixed
threadpool.bulk.size: 20
threadpool.bulk.queue_size: 500

threadpool.index.type: fixed
threadpool.index.size: 20
threadpool.index.queue_size: 1000

threadpool.search.type: fixed
threadpool.search.size: 30
threadpool.search.queue_size: 4000

index.refresh_interval: 10s
index.merge.scheduler.max_thread_count: 1
index.max_result_window: 1000000000
#path.data: {{dataDirs}}
#path.logs: {{logDir}}

network.host: IP
network.publish_host: IP
transport.tcp.port: 9300
http.port: 9200

http.enabled: true
http.cors.allow-origin: "/.*/"

http.cors.enabled: true
index.number_of_shards: 6
index.number_of_replicas: 0

#gateway.type: local
#gateway.recover_after_nodes: 5
#gateway.expected_nodes: 6

cluster.routing.allocation.node_initial_primaries_recoveries: 8
cluster.routing.allocation.node_concurrent_recoveries: 4

indices.recovery.max_bytes_per_sec: 80mb
indices.recovery.concurrent_streams: 5
indices.fielddata.cache.size: 30%
indices.ttl.interval: 43200s
indices.ttl.bulk_size: 100000

#discovery.zen.minimum_master_nodes: {{masterCounts}}
#discovery.zen.ping.timeout: 60s
#discovery.zen.ping.multicast.enabled: false
#discovery.zen.ping.unicast.hosts: {{masters}}

index.translog.flush_threshold_size: 512m
index.translog.flush_threshold_ops: 100000
index.translog.sync_interval: 10s

index.search.slowlog.level: INFO
index.search.slowlog.threshold.query.warn: 10s
index.search.slowlog.threshold.query.info: 5s
index.search.slowlog.threshold.query.debug: 2s
index.search.slowlog.threshold.query.trace: 500ms

index.search.slowlog.threshold.fetch.warn: 1s
index.search.slowlog.threshold.fetch.info: 800ms
index.search.slowlog.threshold.fetch.debug: 500ms
index.search.slowlog.threshold.fetch.trace: 200ms

index.indexing.slowlog.level: INFO
index.indexing.slowlog.threshold.index.warn: 10s
index.indexing.slowlog.threshold.index.info: 5s
index.indexing.slowlog.threshold.index.debug: 2s
index.indexing.slowlog.threshold.index.trace: 500ms
action.destructive_requires_name: true

script.groovy.sandbox.enabled: true
script.inline: on
script.indexed: on
script.search: on
script.engine.groovy.inline.aggs: on
```
## 如何写查询语句
