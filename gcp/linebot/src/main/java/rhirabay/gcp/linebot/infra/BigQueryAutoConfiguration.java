package rhirabay.gcp.linebot.infra;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class BigQueryAutoConfiguration {
    @Bean
    public BigQuery bigQuery() {
        return BigQueryOptions.getDefaultInstance().getService();
    }
}
