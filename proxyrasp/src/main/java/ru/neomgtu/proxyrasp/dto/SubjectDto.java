package ru.neomgtu.proxyrasp.dto;

import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
public class SubjectDto {
    private String uid;
    private String summary;
    private String description;
    private String location;
    private String start;
    private String end;
    private String status;
}

/*
BEGIN:VEVENT
DTSTART:20260224T113500
DTEND:20260224T130500
UID:dd76278fa91e6e53e49c9f85fb3fcf21-group-565@rasp.omgtu.ru
X-MICROSOFT-CDO-BUSYSTATUS:FREE
X-DEVEXPRESS-STATUS:FREE
DTSTAMP:20260225T165600
SUMMARY:Безопасность жизнедеятельности
LOCATION:5-305/УЛК-5
DESCRIPTION:Безопасность жизнедеятельности\nдоц.\, к.н. КОРЧАГИН А.Б. \n \n
 Лабораторные работы \n5-305/УЛК-5
END:VEVENT
*/
