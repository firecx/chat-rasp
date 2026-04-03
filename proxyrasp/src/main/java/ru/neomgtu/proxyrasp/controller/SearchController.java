package ru.neomgtu.proxyrasp.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;
import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.services.SearchService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;


@RestController
@RequestMapping("/api/search")
@RequiredArgsConstructor
public class SearchController {
    
    private final SearchService searchService;

    @GetMapping(value = "/search", produces = "application/json")
    public Mono<String> getMethodName(@RequestParam String term, @RequestParam String type) {
        return searchService.search(term, type);
    }
    
}
