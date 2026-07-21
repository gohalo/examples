package com.example.doris;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * Doris JDBC 访问示例。
 *
 * Doris FE 兼容 MySQL 协议，因此可直接使用 MySQL 的 JDBC 驱动进行连接。
 * URL 中通过逗号列出多个 FE 地址，驱动会在连接时自动进行故障切换（failover）。
 *
 * 会话变量 exec_mem_limit 通过 sessionVariables 参数在建立连接时下发，
 * 也可以在拿到连接后通过 "SET exec_mem_limit=..." 语句设置。
 */
public class DorisJdbcExample {

    // 多个 FE 节点用逗号分隔，实现客户端侧的高可用切换
    private static final String DATABASE = "information_schema";
    // private static final String FE_HOSTS = "10.175.66.124:9030,10.175.82.186:9030";
    // private static final String USER = "root";
    // private static final String PASSWORD = "YourPassword";

    private static final String FE_HOSTS = "music-doris-das.service.gy.ntes:4306";
    private static final String USER = "copyright";
    private static final String PASSWORD = "sK9pR7xQ";

    // 10 GiB = 10 * 1024 * 1024 * 1024 = 10737418240
    private static final long EXEC_MEM_LIMIT = 10737418240L;

    public static void main(String[] args) {
        // 通过 sessionVariables 在连接建立时设置会话变量，等价于每次连接后执行 SET
        String jdbcUrl = String.format(
                "jdbc:mysql://%s/%s"
                        + "?useSSL=false"
                        + "&useUnicode=true"
                        + "&queryTimeoutKillsConnection=false"
                        + "&connectionAttributes=datasource:doris.youdata,proxy_user:youdata_wo_priv,query_timeout:10000"
                        + "&characterEncoding=UTF-8"
                        + "&connectTimeout=5000"
                        + "&socketTimeout=60000"
                        + "&sessionVariables=exec_mem_limit=%d",
                FE_HOSTS, DATABASE, EXEC_MEM_LIMIT);

        System.out.println("JDBC URL: " + jdbcUrl);
        try {
            // MySQL Connector/J 8.x 会自动注册驱动，这里显式加载仅为兼容旧版本
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            System.err.println("MySQL JDBC 驱动未找到，请确认已引入 mysql-connector-java 依赖。");
            e.printStackTrace();
            return;
        }

        try (Connection conn = DriverManager.getConnection(jdbcUrl, USER, PASSWORD);
            Statement stmt = conn.createStatement()) {
            stmt.setQueryTimeout(1);

            // 也可以在此显式再设置一次，确保生效
            stmt.execute("SET exec_mem_limit=" + EXEC_MEM_LIMIT);

            // 验证会话变量是否已经设置成功
            try (ResultSet rs = stmt.executeQuery("SHOW VARIABLES LIKE 'exec_mem_limit'")) {
                while (rs.next()) {
                    System.out.printf("Session variable %s = %s%n",
                            rs.getString(1), rs.getString(2));
                }
            }

            // 执行 SLEEP 函数：让查询在服务端阻塞若干秒，可用于观察 query_timeout 是否生效
            long sleepSeconds = 2;
            long beforeSleep = System.currentTimeMillis();
            try (ResultSet rs = stmt.executeQuery("SELECT SLEEP(" + sleepSeconds + ")")) {
                while (rs.next()) {
                    System.out.printf("SLEEP(%d) returned %s, elapsed %d ms%n",
                            sleepSeconds, rs.getString(1),
                            System.currentTimeMillis() - beforeSleep);
                }
            }

            // 一条简单查询作为示例
            // try (ResultSet rs = stmt.executeQuery("SELECT CURRENT_TIMESTAMP() AS now, VERSION() AS version")) {
            //     while (rs.next()) {
            //         System.out.printf("Doris now=%s, version=%s%n",
            //                 rs.getString("now"), rs.getString("version"));
            //     }
            // }
        } catch (SQLException e) {
            System.err.println("访问 Doris 集群失败：" + e.getMessage());
            e.printStackTrace();
        }
    }
}
