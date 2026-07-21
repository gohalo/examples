# Examples Bundle

Java 示例代码集合，采用 Maven 多模块结构，方便按主题追加新示例。

## 目录结构

```
Java/Bundle/
├── pom.xml                # 父 POM，统一依赖与插件版本
├── doris-jdbc/            # 通过 JDBC 访问 Doris 集群
│   ├── pom.xml
│   └── src/main/java/com/example/doris/DorisJdbcExample.java
└── README.md
```

## 现有模块

| 模块 | 说明 |
| ---- | ---- |
| [`doris-jdbc`](./doris-jdbc) | 使用 MySQL JDBC 驱动访问 Doris 集群，演示多 FE 高可用与会话变量 `exec_mem_limit` 设置 |

## 构建

在根目录一次性构建所有模块：

```bash
mvn clean package
```

单独构建某个模块（例如 `doris-jdbc`）：

```bash
mvn -pl doris-jdbc -am clean package
```

产物位于对应模块的 `target/` 目录下。

也可以直接运行。

```bash
mvn -pl doris-jdbc compile exec:java
mvn -pl doris-jdbc compile exec:exec
```

## 新增示例模块

1. 在 `Java/Bundle/` 下新建目录，例如 `kafka-producer/`。
2. 在其中创建 `pom.xml`，`<parent>` 指向根 POM：

   ```xml
   <parent>
       <groupId>com.example</groupId>
       <artifactId>examples-bundle-parent</artifactId>
       <version>1.0.0</version>
       <relativePath>../pom.xml</relativePath>
   </parent>
   <artifactId>kafka-producer</artifactId>
   ```

3. 在根 `pom.xml` 的 `<modules>` 中登记新模块：

   ```xml
   <modules>
       <module>doris-jdbc</module>
       <module>kafka-producer</module>
   </modules>
   ```

4. 通用依赖版本请写到根 POM 的 `<dependencyManagement>` 中，子模块只声明 `groupId`/`artifactId` 即可继承版本。
