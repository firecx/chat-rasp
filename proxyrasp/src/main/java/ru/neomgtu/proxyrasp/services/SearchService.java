package ru.neomgtu.proxyrasp.services;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.interfaces.ExternalSearchServer;

@Service
@RequiredArgsConstructor
public class SearchService {
    
    private final ExternalSearchServer externalSearchServer;

    public Mono<String> search(String term, String type) {
        return externalSearchServer.search(term, type);
    }
}
