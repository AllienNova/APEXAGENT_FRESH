view: business_metrics {
  sql_table_name: `aideon_analytics.business_metrics` ;;
  
  dimension: id {
    primary_key: yes
    type: string
    sql: ${TABLE}.id ;;
  }
  
  dimension: subscription_id {
    type: string
    sql: ${TABLE}.subscription_id ;;
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
  
  dimension: currency {
    type: string
    sql: ${TABLE}.currency ;;
  }
  
  dimension: tier {
    type: string
    sql: ${TABLE}.tier ;;
  }
  
  dimension: payment_method {
    type: string
    sql: ${TABLE}.payment_method ;;
  }
  
  dimension: transaction_type {
    type: string
    sql: ${TABLE}.transaction_type ;;
  }
  
  measure: count {
    type: count
    drill_fields: [id, subscription_id, metric_type, timestamp_date]
  }
  
  measure: total_value {
    type: sum
    sql: ${value} ;;
    value_format_name: usd
  }
  
  measure: average_value {
    type: average
    sql: ${value} ;;
    value_format_name: usd
  }
  
  measure: revenue_basic_tier {
    type: sum
    sql: ${value} ;;
    filters: [tier: "Basic"]
    value_format_name: usd
  }
  
  measure: revenue_pro_tier {
    type: sum
    sql: ${value} ;;
    filters: [tier: "Pro"]
    value_format_name: usd
  }
  
  measure: revenue_expert_tier {
    type: sum
    sql: ${value} ;;
    filters: [tier: "Expert"]
    value_format_name: usd
  }
  
  measure: revenue_enterprise_tier {
    type: sum
    sql: ${value} ;;
    filters: [tier: "Enterprise"]
    value_format_name: usd
  }
}
