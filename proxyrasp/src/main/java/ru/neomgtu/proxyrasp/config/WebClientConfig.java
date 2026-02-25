package ru.neomgtu.proxyrasp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.support.WebClientAdapter;
import org.springframework.web.service.invoker.HttpServiceProxyFactory;



import ru.neomgtu.proxyrasp.interfaces.ExternalScheduleServer;

@Configuration
public class WebClientConfig {
	
        private static final String BASE_URL = "https://rasp.omgtu.ru";

	@Bean
	public ExternalScheduleServer externalScheduleServer() {
	        WebClient webClient = WebClient.builder()
                        .baseUrl(BASE_URL)
                        .build();

                HttpServiceProxyFactory factory =
                        HttpServiceProxyFactory
                                .builderFor(WebClientAdapter.create(webClient))
                                .build();

                return factory.createClient(ExternalScheduleServer.class);
	}
}
