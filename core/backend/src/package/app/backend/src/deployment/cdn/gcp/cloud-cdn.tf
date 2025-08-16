resource "google_compute_backend_bucket" "static_assets" {
  name        = "apexagent-static-assets-${var.environment}"
  description = "Backend bucket for ApexAgent static assets"
  bucket_name = google_storage_bucket.static_assets.name
  enable_cdn  = true

  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    client_ttl        = 3600
    default_ttl       = 86400
    max_ttl           = 31536000
    negative_caching  = true
    serve_while_stale = 86400
  }
}

resource "google_storage_bucket" "static_assets" {
  name          = "apexagent-static-assets-${var.environment}"
  location      = var.region
  force_destroy = var.environment != "production"
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }

  cors {
    origin          = ["https://${var.domain_name}"]
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["Content-Type", "Access-Control-Allow-Origin"]
    max_age_seconds = 3600
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  versioning {
    enabled = var.environment == "production"
  }
}

resource "google_compute_url_map" "cdn" {
  name            = "apexagent-cdn-${var.environment}"
  description     = "URL map for ApexAgent CDN"
  default_service = google_compute_backend_bucket.static_assets.self_link

  host_rule {
    hosts        = [var.domain_name, "www.${var.domain_name}"]
    path_matcher = "main"
  }

  path_matcher {
    name            = "main"
    default_service = google_compute_backend_bucket.static_assets.self_link

    path_rule {
      paths   = ["/static/*", "/images/*", "/assets/*", "/*.js", "/*.css"]
      service = google_compute_backend_bucket.static_assets.self_link
    }

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.api.self_link
    }
  }
}

resource "google_compute_backend_service" "api" {
  name                  = "apexagent-api-backend-${var.environment}"
  description           = "Backend service for ApexAgent API"
  protocol              = "HTTPS"
  timeout_sec           = 30
  enable_cdn            = false
  connection_draining_timeout_sec = 300
  health_checks         = [google_compute_health_check.api.id]
  load_balancing_scheme = "EXTERNAL"

  backend {
    group = google_compute_instance_group.api.self_link
    balancing_mode  = "UTILIZATION"
    capacity_scaler = 1.0
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

resource "google_compute_health_check" "api" {
  name               = "apexagent-api-health-check-${var.environment}"
  description        = "Health check for ApexAgent API"
  timeout_sec        = 5
  check_interval_sec = 10
  healthy_threshold  = 2
  unhealthy_threshold = 3

  https_health_check {
    port         = "443"
    request_path = "/health"
  }
}

resource "google_compute_instance_group" "api" {
  name        = "apexagent-api-instance-group-${var.environment}"
  description = "Instance group for ApexAgent API servers"
  zone        = "${var.region}-a"
  network     = google_compute_network.vpc.self_link

  named_port {
    name = "https"
    port = 443
  }
}

resource "google_compute_global_address" "cdn_ip" {
  name        = "apexagent-cdn-ip-${var.environment}"
  description = "Global IP address for ApexAgent CDN"
}

resource "google_compute_managed_ssl_certificate" "cdn" {
  name = "apexagent-cdn-cert-${var.environment}"

  managed {
    domains = [var.domain_name, "www.${var.domain_name}"]
  }
}

resource "google_compute_target_https_proxy" "cdn" {
  name             = "apexagent-cdn-https-proxy-${var.environment}"
  url_map          = google_compute_url_map.cdn.self_link
  ssl_certificates = [google_compute_managed_ssl_certificate.cdn.self_link]
}

resource "google_compute_global_forwarding_rule" "cdn_https" {
  name       = "apexagent-cdn-https-rule-${var.environment}"
  target     = google_compute_target_https_proxy.cdn.self_link
  port_range = "443"
  ip_address = google_compute_global_address.cdn_ip.address
}

resource "google_compute_url_map" "http_redirect" {
  name = "apexagent-http-redirect-${var.environment}"
  description = "URL map for HTTP to HTTPS redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "http_redirect" {
  name    = "apexagent-http-redirect-proxy-${var.environment}"
  url_map = google_compute_url_map.http_redirect.self_link
}

resource "google_compute_global_forwarding_rule" "http_redirect" {
  name       = "apexagent-http-redirect-rule-${var.environment}"
  target     = google_compute_target_http_proxy.http_redirect.self_link
  port_range = "80"
  ip_address = google_compute_global_address.cdn_ip.address
}

resource "google_storage_bucket_iam_binding" "cdn_viewer" {
  bucket = google_storage_bucket.static_assets.name
  role   = "roles/storage.objectViewer"
  members = [
    "allUsers",
  ]
}

resource "google_compute_security_policy" "cdn_security_policy" {
  name        = "apexagent-cdn-security-policy-${var.environment}"
  description = "Security policy for ApexAgent CDN"

  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "XSS attack protection"
  }

  rule {
    action   = "deny(403)"
    priority = "1001"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "SQL injection protection"
  }

  rule {
    action   = "throttle"
    priority = "2000"
    match {
      expr {
        expression = "request.headers['user-agent'].contains('bot') || request.headers['user-agent'].contains('crawler')"
      }
    }
    description = "Rate limit bots and crawlers"
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 10
        interval_sec = 60
      }
    }
  }

  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default rule, allow all traffic"
  }
}

output "cdn_ip_address" {
  value       = google_compute_global_address.cdn_ip.address
  description = "IP address of the CDN"
}

output "cdn_url" {
  value       = "https://${var.domain_name}"
  description = "URL of the CDN"
}

output "storage_bucket_name" {
  value       = google_storage_bucket.static_assets.name
  description = "Name of the storage bucket for static assets"
}
