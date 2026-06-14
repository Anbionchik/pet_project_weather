FROM eclipse-temurin:19-jre

ENV MB_PLUGINS_DIR=/home/plugins/

ADD https://downloads.metabase.com/v0.49.3/metabase.jar /home/metabase.jar

ADD https://github.com/MotherDuck-Open-Source/metabase_duckdb_driver/releases/download/0.2.12-b/duckdb.metabase-driver.jar /home/plugins/

RUN chmod 744 /home/plugins/duckdb.metabase-driver.jar

CMD ["java", "-jar", "/home/metabase.jar"]