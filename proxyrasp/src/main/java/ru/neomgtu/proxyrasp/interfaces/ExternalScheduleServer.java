package ru.neomgtu.proxyrasp.interfaces;

import java.util.List;

import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.service.annotation.GetExchange;
import org.springframework.web.service.annotation.HttpExchange;

import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.dto.SubjectDto;

@HttpExchange(url = "/api/schedule")
public interface ExternalScheduleServer {

    @GetExchange("/group/{groupId}")
    Mono<List<SubjectDto>> getScheduleByGroupId(
        @PathVariable String groupId,
        @RequestParam String start,
        @RequestParam String finish,
        @RequestParam int lng
    );

    @GetExchange("/person/{personId}")
    Mono<List<SubjectDto>> getScheduleByPersonId(
        @PathVariable String personId,
        @RequestParam String start,
        @RequestParam String finish,
        @RequestParam int lng
    );

}
