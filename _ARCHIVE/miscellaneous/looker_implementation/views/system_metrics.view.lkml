view: system_metrics {
  sql_table_name: `aideon_analytics.system_metrics` ;;
  
  dimension: id {
    primary_key: yes
    type: string
    sql: ${TABLE}.id ;;
  }
  
  dimension: component {
    type: string
    sql: ${TABLE}.component ;;
  }
  
  dimension: metric_type {
    type: string
    sql: ${TABLE}.metric_type ;;
  }
  
  dimension_group: timestamp {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.timestamp ;;
  }
  
  dimension: value {
    type: number
    sql: ${TABLE}.value ;;
  }
  
  dimension: unit {
    type: string
    sql: ${TABLE}.unit ;;
  }
  
  dimension: environment {
    type: string
    sql: ${TABLE}.environment ;;
  }
  
  dimension: instance_id {
    type: string
    sql: ${TABLE}.instance_id ;;
  }
  
  dimension: status {
    type: string
    sql: ${TABLE}.status ;;
  }
  
  measure: count {
    type: count
    drill_fields: [id, component, metric_type, timestamp_date]
  }
  
  measure: average_value {
    type: average
    sql: ${value} ;;
    value_format_name: decimal_2
  }
  
  measure: max_value {
    type: max
    sql: ${value} ;;
    value_format_name: decimal_2
  }
  
  measure: min_value {
    type: min
    sql: ${value} ;;
    value_format_name: decimal_2
  }
  
  measure: error_count {
    type: count
    filters: [status: "error"]
  }
  
  measure: warning_count {
    type: count
    filters: [status: "warning"]
  }
}
