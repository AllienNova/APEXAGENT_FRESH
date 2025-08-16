view: model_performance {
  sql_table_name: `aideon_analytics.model_performance` ;;
  
  dimension: id {
    primary_key: yes
    type: string
    sql: ${TABLE}.id ;;
  }
  
  dimension: model_id {
    type: string
    sql: ${TABLE}.model_id ;;
  }
  
  dimension: request_id {
    type: string
    sql: ${TABLE}.request_id ;;
  }
  
  dimension: user_id {
    type: string
    sql: ${TABLE}.user_id ;;
  }
  
  dimension_group: timestamp {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.timestamp ;;
  }
  
  dimension: latency_ms {
    type: number
    sql: ${TABLE}.latency_ms ;;
  }
  
  dimension: tokens_input {
    type: number
    sql: ${TABLE}.tokens_input ;;
  }
  
  dimension: tokens_output {
    type: number
    sql: ${TABLE}.tokens_output ;;
  }
  
  dimension: success {
    type: yesno
    sql: ${TABLE}.success ;;
  }
  
  dimension: error_type {
    type: string
    sql: ${TABLE}.error_type ;;
  }
  
  dimension: error_message {
    type: string
    sql: ${TABLE}.error_message ;;
  }
  
  dimension: cost {
    type: number
    sql: ${TABLE}.cost ;;
    value_format_name: usd
  }
  
  measure: count {
    type: count
    drill_fields: [id, model_id, timestamp_date, success]
  }
  
  measure: average_latency {
    type: average
    sql: ${latency_ms} ;;
    value_format_name: decimal_2
  }
  
  measure: p95_latency {
    type: percentile
    percentile: 95
    sql: ${latency_ms} ;;
    value_format_name: decimal_2
  }
  
  measure: success_rate {
    type: number
    sql: 1.0 * SUM(IF(${success}, 1, 0)) / NULLIF(COUNT(*), 0) ;;
    value_format_name: percent_2
  }
  
  measure: total_tokens_input {
    type: sum
    sql: ${tokens_input} ;;
  }
  
  measure: total_tokens_output {
    type: sum
    sql: ${tokens_output} ;;
  }
  
  measure: total_cost {
    type: sum
    sql: ${cost} ;;
    value_format_name: usd
  }
}
