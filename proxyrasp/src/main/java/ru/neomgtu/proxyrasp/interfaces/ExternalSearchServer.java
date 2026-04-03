package ru.neomgtu.proxyrasp.interfaces;

import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.service.annotation.GetExchange;
import org.springframework.web.service.annotation.HttpExchange;

import reactor.core.publisher.Mono;

@HttpExchange(url = "/api/search")
public interface ExternalSearchServer {
    
    @GetExchange()
    Mono<String> search(
        @RequestParam String term,
        @RequestParam String type
    );
}
