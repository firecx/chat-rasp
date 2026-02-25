package ru.neomgtu.proxyrasp.services;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.interfaces.ExternalScheduleServer;

@Service
@RequiredArgsConstructor
public class ScheduleService {

    private final ExternalScheduleServer externalScheduleServer;

    public Mono<String> getScheduleByGroupId(String groupId, String start, String finish, int lng) {
        return externalScheduleServer.getScheduleByGroupId(groupId, start, finish, lng);
    }
}
