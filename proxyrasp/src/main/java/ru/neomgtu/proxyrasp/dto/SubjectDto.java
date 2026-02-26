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
}
