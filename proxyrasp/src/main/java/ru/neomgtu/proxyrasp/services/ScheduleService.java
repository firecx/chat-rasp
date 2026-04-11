package ru.neomgtu.proxyrasp.services;

import java.util.List;

import org.springframework.stereotype.Service;

import lombok.RequiredArgsConstructor;
import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.dto.SubjectDto;
import ru.neomgtu.proxyrasp.interfaces.ExternalScheduleServer;

@Service
@RequiredArgsConstructor
public class ScheduleService {

    private final ExternalScheduleServer externalScheduleServer;
    
    public Mono<List<SubjectDto>> getScheduleByGroupId(String groupId, String start, String finish, int lng) {
        return externalScheduleServer.getScheduleByGroupId(groupId, start, finish, lng);
    }

    public Mono<List<SubjectDto>> getScheduleByPersonId(String personId, String start, String finish, int lng) {
        return externalScheduleServer.getScheduleByPersonId(personId, start, finish, lng);
    }
}
