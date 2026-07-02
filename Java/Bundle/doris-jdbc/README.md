# doris-jdbc

通过 MySQL JDBC 驱动访问 Doris 集群，并在会话中设置 `exec_mem_limit=10737418240`（10 GiB）。

## 集群信息

- FE 节点：`10.175.66.124:9030`、`10.175.82.186:9030`
- 协议：Doris FE 兼容 MySQL 协议
- 驱动：`mysql-connector-java`（版本由父 POM 统一管理）

## 关键实现

1. **多 FE 高可用**：JDBC URL 用逗号列出多个 host，驱动自动做故障切换。

   ```
   jdbc:mysql://10.175.66.124:9030,10.175.82.186:9030/information_schema?...
   ```

2. **设置会话变量**：URL 追加 `sessionVariables=exec_mem_limit=10737418240`，
   连接建立时自动执行 `SET exec_mem_limit=10737418240`。代码里同时通过
   `Statement.execute("SET exec_mem_limit=...")` 显式设置一次做兜底。

## 构建与运行

在 `Java/Bundle/` 根目录执行：

```bash
mvn -pl doris-jdbc -am clean package
java -jar doris-jdbc/target/doris-jdbc-1.0.0.jar
```

修改用户名/密码请编辑 `src/main/java/com/example/doris/DorisJdbcExample.java` 中的
`USER` / `PASSWORD` 常量。
