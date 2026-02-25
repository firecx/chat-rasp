package ru.neomgtu.proxyrasp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.fasterxml.jackson.databind.ObjectMapper;

import net.fortuna.ical4j.data.CalendarBuilder;

@Configuration
public class IcsToJsonVeventsMapperConfig {

    @Bean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }

    @Bean
    public CalendarBuilder calendarBuilder() {
        return new CalendarBuilder();
    }
}
