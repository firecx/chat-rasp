package ru.neomgtu.proxyrasp.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;
import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.services.ScheduleService;

@RestController
@RequestMapping("/api/schedule")
@RequiredArgsConstructor
public class ScheduleController {

    private final ScheduleService scheduleService;

    @GetMapping("/group/{groupId}")
    public Mono<String> getGroupSchedule(
            @PathVariable String groupId,
            @RequestParam String start,
            @RequestParam String finish,
            @RequestParam int lng) {
        return scheduleService.getScheduleByGroupId(groupId, start, finish, lng);
    }

}
