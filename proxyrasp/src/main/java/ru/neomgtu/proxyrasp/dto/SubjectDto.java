package ru.neomgtu.proxyrasp.dto;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

import lombok.Data;
import lombok.experimental.Accessors;

@Data
@Accessors(chain = true)
@JsonIgnoreProperties(ignoreUnknown = true)
public class SubjectDto {
    private String auditorium; //Аудитория
    private String beginLesson; //Время начала занятия
    private String building; //Корпус
    private String createddate; //Дата создания расписания
    private String date; //Дата занятия
    private String dayOfWeek; //Номер дня недели
    private String dayOfWeekString; //День недели
    private String discipline; //Название дисциплины
    private String endLesson; //Время конца занятия
    private String kindOfWork; //Тип занятия
    private String lecturer; //Преподаватель
    private String modifieddate; //Дата последнего изменения расписания
    private String stream; //Поток групп
    private String subGroup; //Подгруппа
    private List<Object> listGroups; //Список групп
}
