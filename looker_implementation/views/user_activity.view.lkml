view: user_activity {
  sql_table_name: `aideon_analytics.user_activity` ;;
  
  dimension: id {
    primary_key: yes
    type: string
    sql: ${TABLE}.id ;;
  }
  
  dimension: user_id {
    type: string
    sql: ${TABLE}.user_id ;;
  }
  
  dimension: session_id {
    type: string
    sql: ${TABLE}.session_id ;;
  }
  
  dimension: feature_id {
    type: string
    sql: ${TABLE}.feature_id ;;
  }
  
  dimension: activity_type {
    type: string
    sql: ${TABLE}.activity_type ;;
  }
  
  dimension_group: timestamp {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.timestamp ;;
  }
  
  dimension: duration_seconds {
    type: number
    sql: ${TABLE}.duration_seconds ;;
  }
  
  dimension: success {
    type: yesno
    sql: ${TABLE}.success ;;
  }
  
  dimension: error_code {
    type: string
    sql: ${TABLE}.error_code ;;
  }
  
  dimension: device_type {
    type: string
    sql: ${TABLE}.device_type ;;
  }
  
  dimension: browser {
    type: string
    sql: ${TABLE}.browser ;;
  }
  
  dimension: location {
    type: string
    sql: ${TABLE}.location ;;
  }
  
  measure: count {
    type: count
    drill_fields: [id, user_id, activity_type, timestamp_date]
  }
  
  measure: average_duration {
    type: average
    sql: ${duration_seconds} ;;
    value_format_name: decimal_2
  }
  
  measure: success_rate {
    type: number
    sql: 1.0 * SUM(IF(${success}, 1, 0)) / NULLIF(COUNT(*), 0) ;;
    value_format_name: percent_2
  }
  
  measure: distinct_users {
    type: count_distinct
    sql: ${user_id} ;;
  }
  
  measure: distinct_sessions {
    type: count_distinct
    sql: ${session_id} ;;
  }
}
