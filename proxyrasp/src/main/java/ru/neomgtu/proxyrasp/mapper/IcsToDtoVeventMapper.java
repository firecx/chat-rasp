package ru.neomgtu.proxyrasp.mapper;

import org.springframework.stereotype.Component;

import net.fortuna.ical4j.model.component.VEvent;
import net.fortuna.ical4j.model.property.DtEnd;
import net.fortuna.ical4j.model.property.DtStart;
import ru.neomgtu.proxyrasp.dto.SubjectDto;

@Component
public class IcsToDtoVeventMapper {
    public SubjectDto toSubjectDto(VEvent event) {

        SubjectDto subjectDto = new SubjectDto();

        // Simple properties
        subjectDto.setUid(event.getUid() != null ? event.getUid().toString() : null);
        subjectDto.setSummary(event.getSummary() != null ? event.getSummary().getValue() : null);
        subjectDto.setDescription(event.getDescription() != null ? event.getDescription().getValue() : null);
        subjectDto.setLocation(event.getLocation() != null ? event.getLocation().getValue() : null);
        subjectDto.setStatus(event.getStatus() != null ? event.getStatus().getValue() : null);

        // START
        DtStart<?> start = event.getDateTimeStart();
        if (start != null && start.getValue() != null) {
            subjectDto.setStart(start.getValue().toString());
        } else {
            subjectDto.setStart(null);
        }

        // END
        DtEnd<?> end = event.getDateTimeEnd();
        if (end != null && end.getValue() != null) {
            subjectDto.setEnd(end.getValue().toString());
        } else {
            subjectDto.setEnd(null);
        }

        return subjectDto;
    }
}
