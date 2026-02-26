package ru.neomgtu.proxyrasp.services;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.interfaces.ExternalScheduleServer;
import ru.neomgtu.proxyrasp.mapper.IcsToJsonVeventsMapper;

@Service
@RequiredArgsConstructor
public class ScheduleService {

    private final ExternalScheduleServer externalScheduleServer;
    private final IcsToJsonVeventsMapper icsToJsonVeventsMapper;
    

    public Mono<String> getScheduleByGroupId(String groupId, String start, String finish, int lng) {
        return icsToJsonVeventsMapper.convertToJson(
            externalScheduleServer.getScheduleByGroupId(groupId, start, finish, lng)
        );
    }
}
