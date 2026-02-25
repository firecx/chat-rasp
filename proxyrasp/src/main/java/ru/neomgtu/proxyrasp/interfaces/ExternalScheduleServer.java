package ru.neomgtu.proxyrasp.interfaces;

import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.service.annotation.GetExchange;
import org.springframework.web.service.annotation.HttpExchange;

import reactor.core.publisher.Mono;

@HttpExchange(url = "/api/schedule")
public interface ExternalScheduleServer {

    @GetExchange("/group/{groupId}.ics")
    Mono<String> getScheduleByGroupId(
            @PathVariable String groupId,
            @RequestParam String start,
            @RequestParam String finish,
            @RequestParam int lng
    );

}
