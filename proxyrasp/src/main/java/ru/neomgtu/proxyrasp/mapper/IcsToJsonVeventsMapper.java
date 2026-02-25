package ru.neomgtu.proxyrasp.mapper;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

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
                //icsContent = cleanIcs(icsContent);
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
                throw new RuntimeException(e);
            }
        });
    }

    public static String cleanIcs(String icsContent) {
        // 1. Убираем пустые VTIMEZONE
        icsContent = icsContent.replaceAll("(?s)BEGIN:VTIMEZONE.*?END:VTIMEZONE\\s*", "");

        // 2. Экранируем запятые и переносы строк в DESCRIPTION и SUMMARY
        Pattern propPattern = Pattern.compile("(?m)^(DESCRIPTION|SUMMARY):(.*)$");
        Matcher matcher = propPattern.matcher(icsContent);
        StringBuffer sb = new StringBuffer();

        while (matcher.find()) {
            String propName = matcher.group(1);
            String propValue = matcher.group(2).trim(); // убираем лишние пробелы
            // экранируем запятые, точку с запятой и переносы строк
            propValue = propValue.replace("\\", "\\\\")    // слеши экранируем
                                 .replace(",", "\\,")
                                 .replace(";", "\\;")
                                 .replace("\n", "\\n");
            matcher.appendReplacement(sb, propName + ":" + propValue);
        }
        matcher.appendTail(sb);

        // 3. Убираем пробелы в начале строк свойств
        String cleaned = sb.toString().replaceAll("(?m)^\\s+", "");

        cleaned = cleaned.replaceAll("(?m)^(DTSTAMP|DTSTART|DTEND):([0-9]{8}T[0-9]{6})$", "$1:$2Z");

        return cleaned;
    }
}
