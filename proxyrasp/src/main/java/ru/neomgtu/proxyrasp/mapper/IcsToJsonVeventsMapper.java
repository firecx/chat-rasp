package ru.neomgtu.proxyrasp.mapper;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.RequiredArgsConstructor;
import net.fortuna.ical4j.data.CalendarBuilder;
import net.fortuna.ical4j.model.Calendar;
import net.fortuna.ical4j.model.Component;
import net.fortuna.ical4j.model.component.VEvent;
import reactor.core.publisher.Mono;
import ru.neomgtu.proxyrasp.dto.SubjectDto;


@org.springframework.stereotype.Component
@RequiredArgsConstructor
public class IcsToJsonVeventsMapper {
    private final IcsToDtoVeventMapper icsToDtoVeventMapper;
    private final ObjectMapper jsonObjectMapper;
    private final CalendarBuilder calendarBuilder;

    public Mono<String> convertToJson(Mono<String> icsContentMono) {
        return icsContentMono.map(icsContent -> {
            try {
                List<SubjectDto> dtoList = new ArrayList<>();
                icsContent = cleanIcs(icsContent);
                Calendar calendar = calendarBuilder.build(
                    new ByteArrayInputStream(icsContent.getBytes(StandardCharsets.UTF_8))
                );

                for (Component component : calendar.getComponents(Component.VEVENT)) {
                    if (component instanceof VEvent vevent) {
                        dtoList.add(icsToDtoVeventMapper.toSubjectDto(vevent));
                    }
                }

                return jsonObjectMapper.writeValueAsString(dtoList);
            } catch (Exception e) {
                System.err.println("\nError parsing ICS content: " + e.getMessage() + "\n");
                throw new RuntimeException(e);
            }
        });
    }

    public static String cleanIcs(String icsContent) {
        // 1. Убираем пустые VTIMEZONE
        icsContent = icsContent.replaceAll("(?s)BEGIN:VTIMEZONE.*?END:VTIMEZONE\\s*", "");

        icsContent = icsContent.replaceAll("(DTSTART|DTEND|DTSTAMP):([0-9T]+)", "$1:$2Z");
        return icsContent;
    }
}
