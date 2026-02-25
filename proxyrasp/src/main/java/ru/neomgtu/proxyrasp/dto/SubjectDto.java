package ru.neomgtu.proxyrasp.dto;

import java.time.LocalDateTime;

import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
public class SubjectDto {
    private String uid;
    private String summary;
    private String description;
    private String location;
    private LocalDateTime start;
    private LocalDateTime end;
    private String timezone;
    private String status;
}
