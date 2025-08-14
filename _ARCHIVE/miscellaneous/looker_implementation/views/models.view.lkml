view: models {
  sql_table_name: `aideon_analytics.models` ;;
  
  dimension: id {
    primary_key: yes
    type: string
    sql: ${TABLE}.id ;;
  }
  
  dimension: name {
    type: string
    sql: ${TABLE}.name ;;
  }
  
  dimension: provider_id {
    type: string
    sql: ${TABLE}.provider_id ;;
  }
  
  dimension: model_type {
    type: string
    sql: ${TABLE}.model_type ;;
  }
  
  dimension: version {
    type: string
    sql: ${TABLE}.version ;;
  }
  
  dimension: parameters {
    type: string
    sql: ${TABLE}.parameters ;;
  }
  
  dimension_group: created {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.created_at ;;
  }
  
  dimension_group: updated {
    type: time
    timeframes: [raw, time, date, week, month, quarter, year]
    sql: ${TABLE}.updated_at ;;
  }
  
  dimension: is_active {
    type: yesno
    sql: ${TABLE}.is_active ;;
  }
  
  dimension: tier {
    type: string
    sql: ${TABLE}.tier ;;
  }
  
  measure: count {
    type: count
    drill_fields: [id, name, provider_id, model_type]
  }
  
  measure: active_models {
    type: count
    filters: [is_active: "yes"]
  }
}
